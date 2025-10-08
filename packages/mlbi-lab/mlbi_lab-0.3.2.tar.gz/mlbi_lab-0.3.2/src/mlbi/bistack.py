import os, sys, shutil, subprocess, importlib, re
from typing import List, Tuple, Dict, Optional, Any

'''
def _pip_install(pkg: str):
    cmd = [sys.executable, "-m", "pip", "install", pkg]
    if quiet:
        cmd.append("-q")
    subprocess.check_call(cmd)
    return 
'''

def _pip_install(pkg: str, quiet: bool = True, upgrade: bool = False) -> int:
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    if quiet:
        cmd.append("-q")
    cmd.append(pkg)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE if quiet else None,
                          stderr=subprocess.STDOUT if quiet else None, text=True)
    return proc.returncode


def ensure_condacolab(run_install: bool = False, quiet: bool = True) -> Tuple[bool, Optional[Any]]:
    """
    Google Colab 여부를 감지해 condacolab을 준비합니다.

    매개변수
    ----------
    run_install : bool
        True면 condacolab.install()를 실행합니다.
        *주의*: Colab 런타임이 즉시 재시작되며, 이후 코드는 실행되지 않습니다.
    quiet : bool
        pip 설치 시 -q(quiet) 옵션 사용 여부.

    반환
    ----------
    (is_colab, condacolab_module_or_None)
    - is_colab: 현재 환경이 Colab이면 True
    - condacolab_module_or_None: Colab이면 condacolab 모듈(설치/임포트 완료), 아니면 None
    """

    # 1) Colab 감지
    try:
        import google.colab  # type: ignore
        is_colab = True
    except Exception:
        is_colab = "COLAB_RELEASE_TAG" in os.environ

    if not is_colab:
        return False, None

    # 2) condacolab 설치/임포트
    try:
        condacolab = importlib.import_module("condacolab")
    except ModuleNotFoundError:
        _pip_install("condacolab")
        condacolab = importlib.import_module("condacolab")

    # 3) 필요 시 conda 설치 및 런타임 재시작
    if run_install:
        condacolab.install()   # 여기서 Colab 런타임이 재시작됩니다.
        # 재시작되므로 아래 코드는 실행되지 않음

    else:
        # 설치만 하고 환경 점검(재시작 없이)
        try:
            condacolab.check()
        except Exception:
            pass

    return True, condacolab


import os, sys, re, shutil, subprocess
from typing import List, Tuple, Dict, Optional

# -------------------- 공통 유틸 --------------------
def _run(cmd: List[str], capture: bool = True) -> Tuple[int, str]:
    """Run command. Returns (returncode, stdout+stderr text)."""
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        text=True,
        check=False,
    )
    out = (proc.stdout or "").strip() if capture else ""
    return proc.returncode, out

def _is_colab() -> bool:
    try:
        import google.colab  # type: ignore
        return True
    except Exception:
        return "COLAB_RELEASE_TAG" in os.environ

def _which(binname: str) -> Optional[str]:
    return shutil.which(binname)

def _sudo_prefix() -> List[str]:
    try:
        is_root = (os.geteuid() == 0)
    except AttributeError:
        is_root = False
    if is_root or _is_colab():
        return []
    return ["sudo"]

def _print_status(name: str, version: Optional[str], installed_now: bool):
    tag = "installed" if installed_now else "already installed"
    vtxt = version or "unknown-version"
    print(f"{name}: {tag} (v{vtxt})")

# -------------------- 버전 프로브 --------------------
def _probe_version(cmd: List[str], regex: str = r'([0-9]+(?:\.[0-9A-Za-z_-]+)*)') -> Optional[str]:
    code, out = _run(cmd, capture=True)
    if code != 0:
        return None
    m = re.search(regex, out, flags=re.IGNORECASE)
    return m.group(1) if m else out.splitlines()[0].strip() if out else None

def _version_minimap2():    return _probe_version(["minimap2", "--version"])
def _version_bwa():         return _probe_version(["bash","-lc",'bwa 2>&1 | grep -m1 -i "Version"'], r'Version:\s*([^\s]+)')
def _version_bowtie2():     return _probe_version(["bowtie2", "--version"], r'version\s+([0-9][^\s]*)')
def _version_star():        return _probe_version(["STAR", "--version"])
def _version_samtools():    return _probe_version(["bash","-lc","samtools --version | head -n1"], r'samtools\s+([0-9][^\s]*)')
def _version_featureCounts(): return _probe_version(["featureCounts", "-v"], r'featureCounts\s+v?([0-9][^\s]*)')
def _version_stringtie():   return _probe_version(["stringtie", "--version"], r'StringTie\s+v?([0-9][^\s]*)')

# -------------------- Java 버전 --------------------
def _parse_java_version(text: str) -> Optional[Tuple[int,int,int,str]]:
    m = re.search(r'version\s+"(\d+)(?:\.(\d+))?(?:\.(\d+))?', text)
    raw = ""
    if m:
        raw = m.group(0)
        major = int(m.group(1) or 0)
        minor = int(m.group(2) or 0)
        patch = int(m.group(3) or 0)
        if major == 1 and minor >= 8:   # 1.8.x → 8
            major = 8
        return (major, minor, patch, raw)
    m2 = re.search(r'version\s+"1\.8\.', text)
    if m2:
        return (8,0,0,'1.8')
    return None

def _get_java_version() -> Optional[Tuple[int,int,int,str]]:
    code, out = _run(["bash","-lc","java -version"], capture=True)
    if code != 0:
        return None
    # 보통 stderr로 나오지만, 우리는 stdout+stderr 합쳐 받음
    return _parse_java_version(out)

def _ensure_java(required_major: int, prefer: str = "apt", allow_conda_fallback: bool = True) -> str:
    """
    Java가 없거나 major가 낮으면 설치. 성공/기설치 버전 문자열 반환(없으면 "unknown").
    """
    v = _get_java_version()
    if v and v[0] >= required_major:
        return f"{v[0]}.{v[1]}.{v[2]}"

    # 설치 필요
    if prefer == "apt" and _which("apt-get"):
        _run(_sudo_prefix()+["apt-get","update","-y","-qq"])
        pkg = f"openjdk-{required_major}-jdk"
        rc,_ = _run(_sudo_prefix()+["apt-get","install","-y","-qq",pkg])
        if rc == 0:
            v2 = _get_java_version()
            return f"{v2[0]}.{v2[1]}.{v2[2]}" if v2 else "unknown"

        if not allow_conda_fallback:
            return "unknown"

    # conda fallback
    conda = _which("conda")
    if conda:
        _run([conda,"install","-y","-q","-c","conda-forge",f"openjdk={required_major}"])
        v3 = _get_java_version()
        return f"{v3[0]}.{v3[1]}.{v3[2]}" if v3 else "unknown"

    return "unknown"

# -------------------- micromamba(CNVkit용) --------------------
def _ensure_micromamba(prefix: str = "/content/micromamba", quiet: bool = True) -> str:
    """
    Ensure micromamba exists at {prefix}/bin/micromamba.
    1) install.sh 시도 → 실패 시
    2) 바이너리 직접 다운로드로 폴백
    """
    import shutil, subprocess, os

    mm_bin = os.path.join(prefix, "bin", "micromamba")
    if os.path.exists(mm_bin):
        return mm_bin

    os.makedirs(os.path.join(prefix, "bin"), exist_ok=True)

    def _run(cmd):
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # 1) 공식 install.sh 시도
    if shutil.which("curl"):
        cmd = ['bash','-lc', f'curl -fsSL micro.mamba.pm/install.sh | bash -s -- -b -p "{prefix}"']
        r = _run(cmd)
        if not quiet: print(r.stdout)
        if os.path.exists(mm_bin):
            return mm_bin

    # 2) 직접 바이너리 다운로드(아키텍처 자동 선택)
    arch = _run(['bash','-lc','uname -m']).stdout.strip()
    url = "https://micro.mamba.pm/api/micromamba/linux-64/latest"
    if arch in ("aarch64", "arm64"):
        url = "https://micro.mamba.pm/api/micromamba/linux-aarch64/latest"

    if not shutil.which("curl"):
        raise RuntimeError("curl not found; cannot fetch micromamba binary.")
    r2 = _run(['bash','-lc', f'curl -fsSL "{url}" -o "{mm_bin}"'])
    if not quiet: print(r2.stdout)
    _ = _run(['bash','-lc', f'chmod +x "{mm_bin}"'])

    if not os.path.exists(mm_bin):
        raise RuntimeError("micromamba installation failed (binary not found after fallback).")
    return mm_bin


def _cnvkit_version_micromamba(env_name: str, prefix: str) -> Optional[str]:
    mm = _ensure_micromamba(prefix)
    rc,out = _run([mm,"run","-n",env_name,"cnvkit.py","version"])
    return out if rc==0 and out else None

def _install_cnvkit_micromamba(env_name="cnvkit", prefix=None) -> str:
    if prefix is None:
        prefix = "/content/micromamba" if _is_colab() else os.path.expanduser("~/.micromamba")
    # 이미 있으면 버전만
    v = _cnvkit_version_micromamba(env_name, prefix)
    if v:
        _print_status("CNVkit (micromamba env)", v, installed_now=False)
        return v
    # 설치
    mm = _ensure_micromamba(prefix)
    _run([mm,"create","-y","-n",env_name,"-c","conda-forge","-c","bioconda",
          "python=3.10","pandas<2.0","cnvkit=0.9.10"])
    v2 = _cnvkit_version_micromamba(env_name, prefix) or "unknown"
    _print_status("CNVkit (micromamba env)", v2, installed_now=True)
    return v2

# -------------------- APT 패키지 처리 --------------------
def _apt_ensure_and_report():
    # 한 번만 update
    if _which("apt-get"):
        _run(_sudo_prefix()+["apt-get","update","-y","-qq"])
    else:
        print("apt-get not found; skipping APT section.")
        return

    pkgs = [
        # (표시이름, apt패키지, 바이너리, 버전함수)
        ("minimap2", "minimap2", "minimap2", _version_minimap2),
        ("bwa",      "bwa",      "bwa",      _version_bwa),
        ("bowtie2",  "bowtie2",  "bowtie2",  _version_bowtie2),
        ("STAR",     "rna-star", "STAR",     _version_star),
        ("samtools", "samtools", "samtools", _version_samtools),
        ("featureCounts(subread)", "subread","featureCounts", _version_featureCounts),
        ("stringtie","stringtie","stringtie",_version_stringtie),
    ]

    for name, aptpkg, binname, vfunc in pkgs:
        binpath = _which(binname)
        if binpath:
            v = vfunc()
            _print_status(name, v, installed_now=False)
            continue
        # install
        rc,_ = _run(_sudo_prefix()+["apt-get","install","-y","-qq",aptpkg])
        if rc != 0:
            # universe 필요한 경우 한 번 더 시도
            _run(_sudo_prefix()+["add-apt-repository","-y","universe"])
            _run(_sudo_prefix()+["apt-get","update","-y","-qq"])
            rc,_ = _run(_sudo_prefix()+["apt-get","install","-y","-qq",aptpkg])
        v = vfunc() if _which(binname) else None
        _print_status(name, v, installed_now=True)

# -------------------- conda(rMATS) 처리 --------------------
def _conda_rmats(ensure_channels=True):
    conda = _which("conda")
    if not conda:
        print("conda not found; skip rMATS (set up conda/condacolab first if needed).")
        return

    def _conda_list_pkg(pkg: str) -> Optional[str]:
        rc,out = _run([conda,"list",pkg])
        if rc==0 and re.search(rf'^{pkg}\s+([0-9][^\s]*)', out, flags=re.MULTILINE):
            v = re.search(rf'^{pkg}\s+([0-9][^\s]*)', out, flags=re.MULTILINE).group(1)
            return v
        return None

    if ensure_channels:
        _run([conda,"config","--add","channels","bioconda"])
        _run([conda,"config","--add","channels","conda-forge"])
        _run([conda,"config","--set","channel_priority","strict"])

    v = _conda_list_pkg("rmats")
    if v:
        _print_status("rMATS (conda)", v, installed_now=False)
        return

    _run([conda,"install","-y","-q","rmats"])
    v2 = _conda_list_pkg("rmats") or "unknown"
    _print_status("rMATS (conda)", v2, installed_now=True)

# -------------------- 메인 엔트리 --------------------
def setup_bio_stack(
    java_required_major: int = 17,
    java_prefer: str = "apt",              # "apt" or "conda"
    java_allow_conda_fallback: bool = True,
    install_rmats_with_conda: bool = True,
    install_cnvkit_mode: str = "skip" # "micromamba" | "conda" | "skip"
):
    """
    - APT: minimap2, bwa, bowtie2, rna-star, samtools, subread(featureCounts), stringtie
      (없으면 설치, 있으면 버전만 출력)
    - Java: 요구 메이저 버전 미만/미설치면 설치(apt 우선, conda 포백) 후 버전 출력
    - rMATS: conda에서 없으면 설치, 있으면 버전만 출력
    - CNVkit: 기본 micromamba 전용 env에 설치(이미 있으면 버전만 출력)
    """
    # 1) APT 도구들
    _apt_ensure_and_report()

    # 2) Java
    jv = _get_java_version()
    if jv and jv[0] >= java_required_major:
        _print_status(f"Java (requires ≥{java_required_major})", f"{jv[0]}.{jv[1]}.{jv[2]}", installed_now=False)
    else:
        v2 = _ensure_java(java_required_major, prefer=java_prefer, allow_conda_fallback=java_allow_conda_fallback)
        _print_status(f"Java (requires ≥{java_required_major})", v2, installed_now=True)

    # 3) rMATS (conda)
    if install_rmats_with_conda:
        _conda_rmats(ensure_channels=True)

    # 4) CNVkit
    if install_cnvkit_mode == "skip":
        print("CNVkit: skipped")
    elif install_cnvkit_mode == "conda":
        conda = _which("conda")
        if not conda:
            print("CNVkit (conda): conda not found; skipped")
        else:
            # 이미 있는지 확인
            rc,out = _run([conda,"list","cnvkit"])
            m = re.search(r'^cnvkit\s+([0-9][^\s]*)', out, flags=re.MULTILINE)
            if m:
                _print_status("CNVkit (conda)", m.group(1), installed_now=False)
            else:
                _run([conda,"install","-y","-q","-c","bioconda","cnvkit"])
                rc,out = _run([conda,"list","cnvkit"])
                m = re.search(r'^cnvkit\s+([0-9][^\s]*)', out, flags=re.MULTILINE)
                _print_status("CNVkit (conda)", m.group(1) if m else "unknown", installed_now=True)
    else:
        _install_cnvkit_micromamba(env_name="cnvkit",
                                   prefix="/content/micromamba" if _is_colab() else os.path.expanduser("~/.micromamba"))
    return


import sys, subprocess, re
from typing import List, Dict, Optional

try:
    # Py>=3.8
    from importlib import metadata as _im
except Exception:
    import importlib_metadata as _im  # fallback

def _pkg_base_name(pkg: str) -> str:
    """
    'scoda-viz==0.4.20' -> 'scoda-viz'
    'pandas>=2.2' -> 'pandas'
    """
    return re.split(r"==|>=|<=|~=|>|<", pkg, maxsplit=1)[0].strip()

def _get_dist_version(dist_name: str) -> Optional[str]:
    try:
        return _im.version(dist_name)
    except _im.PackageNotFoundError:
        return None

def install_common_pydeps(scodaviz_version: str = "0.4.20",
                          quiet: bool = True,
                          upgrade: bool = False) -> Dict[str, Optional[str]]:
    """
    지정한 scoda-viz 버전과 함께 공통 과학계산/시각화 패키지를 설치.
    - quiet=True  : 설치 로그 최소화
    - upgrade=True: 기존 설치되어 있어도 업그레이드 강행
    반환: {pip_name: installed_version or None}
    """
    specs: List[str] = [
        "gdown",
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "scikit-learn",
        "seaborn",
        "scikit-network",
        "statannot",
        "statannotations",
        "lifelines",
        "plotly",
        "scanpy",
        f"scoda-viz=={scodaviz_version}" if scodaviz_version else "scoda-viz",
    ]

    versions: Dict[str, Optional[str]] = {}

    for spec in specs:
        base = _pkg_base_name(spec)
        cur_v = _get_dist_version(base)

        if cur_v and not upgrade:
            print(f"{base}: already installed (v{cur_v})")
            versions[base] = cur_v
            continue

        rc = _pip_install(spec, quiet=quiet, upgrade=upgrade)
        new_v = _get_dist_version(base)
        if rc == 0 and new_v:
            tag = "upgraded" if (cur_v and upgrade) else "installed"
            print(f"{base}: {tag} (v{new_v})")
            versions[base] = new_v
        else:
            print(f"{base}: install failed")
            versions[base] = None

    return versions

#### Usage ####
'''
## If colab, install condacolab
is_colab, ccl = ensure_condacolab(run_install=True)

## With conda installed, setup bio-info packages
setup_bio_stack(
    java_required_major=17,
    java_prefer="apt",              # apt 우선
    java_allow_conda_fallback=True, # apt 실패 시 conda-forge openjdk로
    install_rmats_with_conda=True,
    install_cnvkit_mode="skip"  # "conda", "micromamba" 또는 "skip"도 가능
)

## Install required python packages
# 1) 기본 설치(이미 있으면 스킵), scoda-viz는 0.4.20 고정
install_common_pydeps(scodaviz_version="0.4.20", quiet=True, upgrade=False)

# 2) 조용하지 않게 로그도 보고 싶다면
# install_common_pydeps(scodaviz_version="0.4.20", quiet=False)

# 3) 전부 최신으로 강제 업그레이드
# install_common_pydeps(scodaviz_version="0.4.20", upgrade=True)
'''
