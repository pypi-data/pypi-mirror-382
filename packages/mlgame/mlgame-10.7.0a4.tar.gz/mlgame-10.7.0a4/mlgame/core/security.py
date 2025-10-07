from mlgame.utils.logger import logger
# 安全鎖：禁止所有 exec*（subprocess.run 最終會被擋）
def install_exec_killer():
    import sys
    logger.info(f"您的作業系統是: {sys.platform}")
    if sys.platform == "win32":
        return  # Windows 不適用 seccomp
    elif sys.platform == "darwin":
        return  # MacOS 不適用 seccomp
    
    logger.info("您的作業系統是 Linux，安裝 exec killer 以防止 execve 被使用")

    import pyseccomp as sc
    from pyseccomp import Arch
    import errno
    # 可選：先設 no_new_privs，避免繞過（多數容器已預設開）
    try:
        import ctypes
        libc = ctypes.CDLL(None)
        PR_SET_NO_NEW_PRIVS = 38
        libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
    except Exception:
        pass

    try:
        if hasattr(sc, "SCMP_ACT_ALLOW"):  # A 類：libseccomp 綁定（python3-libseccomp）
            logger.info("libseccomp 綁定，禁止使用 execve")
            flt = sc.SyscallFilter(defaction=sc.SCMP_ACT_ALLOW)
            flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execve"))
            # flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execveat"))
            # （如需要可再加 posix_spawn/posix_spawnp，視 libc 而定）
            flt.load()
        else:  # B 類：pyseccomp 綁定（pip: pyseccomp）
            logger.info("pyseccomp 綁定，禁止使用 execve")
            flt = sc.SyscallFilter(defaction=sc.ALLOW)
            
            # flt.add_rule(sc.ERRNO(errno.EPERM), "execveat")
            flt.add_rule(sc.ERRNO(errno.EPERM), "execve")
            flt.load()
    except Exception as e:
        logger.exception(f"Exception: {e}")


# guard.py
import sys

def lock_exec_linux_with_seccomp():
    # 僅 Linux 才嘗試 seccomp；macOS 直接跳過
    if sys.platform != "linux":
        return False
    try:
        import seccomp as sc
    except Exception:
        return False  # 沒裝 pyseccomp，就回報沒上鎖

    # 安裝 seccomp：禁止 execve/execveat
    if hasattr(sc, "SCMP_ACT_ALLOW"):
        flt = sc.SyscallFilter(defaction=sc.SCMP_ACT_ALLOW)
        flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execve"))
        flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execveat"))
        flt.load()
    else:
        flt = sc.SyscallFilter(defaction=sc.ALLOW)
        flt.add_rule(sc.ERRNO, "execve")
        flt.add_rule(sc.ERRNO, "execveat")
        flt.load()
    return True

def lock_exec_userspace_fallback():
    # macOS / 無 seccomp 時的替代方案（可被繞過，開發/測試用）
    import builtins, subprocess, os

    # 1) PEP 578 audit hook：攔常見事件
    try:
        def _audit_hook(event, args):
            if event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
                raise PermissionError("subprocess/exec is blocked by policy")
            # 可選：也擋 socket 連線
            if event in ("socket.__init__", "socket.connect"):
                raise PermissionError("network is blocked by policy")
        sys.addaudithook(_audit_hook)
    except Exception:
        pass

    # 2) 保險：monkey patch 常用 API（避免沒觸發 audit 的路徑）
    def _blocked(*a, **k):
        raise PermissionError("blocked by policy")
    for name in ("Popen", "call", "check_call", "check_output", "run", "getoutput", "getstatusoutput"):
        if hasattr(subprocess, name):
            setattr(subprocess, name, _blocked)
    for name in ("execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp", "execvpe", "posix_spawn", "posix_spawnp"):
        if hasattr(os, name):
            setattr(os, name, _blocked)

def harden_startup():
    # 1) 盡量用 fork，避免 spawn/exec
    if sys.platform != "win32":
        import multiprocessing as mp
        try:
            mp.set_start_method("fork", force=True)
        except RuntimeError:
            pass

    # 2) 先嘗試 Linux seccomp；失敗就用 fallback
    if not lock_exec_linux_with_seccomp():
        lock_exec_userspace_fallback()