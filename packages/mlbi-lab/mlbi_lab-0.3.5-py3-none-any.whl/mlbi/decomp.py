import os
import shutil
from pathlib import Path
from typing import Optional
import gdown, gzip, shutil, os, tarfile, zipfile

def download_from_google_drive( file_id, out_path = 'downloaded', verbose = True ):
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    gdown.download(url, out_path, quiet = (not verbose))
    return out_path

'''
def decompress_gz( file_in, file_out, remove_gz = True ):
    try:
        with gzip.open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                if remove_gz:
                    os.remove(file_in)
                print(f'File saved to: {file_out}')
                return file_out
    except:
        return None
'''

def decompress_gz(
    file_in: str,
    file_out: Optional[str] = None,
    remove_gz: bool = True,
    overwrite: bool = True,
    buffer_size: int = 1024 * 1024,
    raise_on_error: bool = True,
) -> Optional[str]:
    """
    .gz 파일을 압축 해제합니다.
    - file_out 미지정 시: 입력 파일의 마지막 '.gz'만 제거한 이름으로 저장
      예) 'reads.fastq.gz' -> 'reads.fastq'
    - overwrite=False면, 출력 파일이 이미 있으면 에러
    - remove_gz=True면 성공 후 원본 .gz 삭제
    - 실패 시 None 반환(raise_on_error=True면 예외 발생)

    Returns: 출력 파일 경로(str) 또는 실패 시 None
    """
    try:
        p_in = Path(file_in)

        # 출력 경로 결정
        if file_out is None:
            if p_in.suffix == ".gz":
                p_out = p_in.with_suffix("")           # .gz만 제거
            elif p_in.name.endswith(".gz"):
                p_out = p_in.with_name(p_in.name[:-3]) # 예외적 케이스 대비
            else:
                # .gz가 아님: 마지막 확장자 제거(또는 그대로 저장 원하면 여기 수정)
                p_out = p_in.with_suffix("")
        else:
            p_out = Path(file_out)

        if p_out.exists() and not overwrite:
            raise FileExistsError(f"Output exists: {p_out} (set overwrite=True to replace)")

        # 압축 해제
        with gzip.open(p_in, "rb") as f_in, open(p_out, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=buffer_size)

        # 원본 삭제 옵션
        if remove_gz and p_in.exists():
            try:
                p_in.unlink()
            except Exception:
                pass

        print(f"File saved to: {p_out}")
        return str(p_out)

    except Exception as e:
        # 부분적으로 생성된 파일 정리
        try:
            if 'p_out' in locals() and p_out.exists():
                p_out.unlink()
        except Exception:
            pass
        if raise_on_error:
            raise
        print(f"decompress_gz error: {e}")
        return None

'''
def decompress_zip(file_in, extract_dir = './', remove_zip = True ):
    try:
        with zipfile.ZipFile(file_in, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            if remove_zip:
                os.remove(file_in)
            print(f'Files extracted to: {extract_dir}')
            return extract_dir
    except:
        return None
'''

def decompress_zip(file_in, extract_dir='extract_tmp', remove_zip=True):
    try:
        with zipfile.ZipFile(file_in, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            extracted_files = zip_ref.namelist()

        if len(extracted_files) > 1:
            print("More than one files in Zip .")
            flst = os.listdir(extract_dir)
            if len(flst) == 1:
                shutil.move(os.path.join(extract_dir, flst[0]), '.')
            else:
                # shutil.move(extract_dir, '.'.join(file_in.split('.')[:-1]))
                for f in flst:
                    ft = extract_dir + '/%s' % f
                    shutil.move(ft, '.')
                    
            shutil.rmtree(extract_dir)
            return 

        else:
            # 압축 해제된 파일 경로
            extracted_path = os.path.join(extract_dir, extracted_files[0])
    
            # 이동 대상 경로 (현재 작업 디렉토리로 이동)
            file_out = os.path.basename(extracted_files[0])
            shutil.move(extracted_path, file_out)
    
            # 압축 해제 폴더 및 zip 파일 제거 (옵션)
            if remove_zip:
                os.remove(file_in)
            shutil.rmtree(extract_dir)
    
            return file_out

    except Exception as e:
        print(f"오류 발생: {e}")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        return None


def decompress_tar_gz( file_in, remove_org = True ):

    try:
        extract_path = 'extract_tmp'
        if os.path.isdir(extract_path):
            shutil.rmtree(extract_path)
    
        with tarfile.open(file_in, "r:gz") as tar:
            tar.extractall(path=extract_path)

        flst = os.listdir(extract_path)
        if len(flst) > 1:
            for f in flst:
                ft = extract_path + '/%s' % f
                shutil.move(ft, '.')
            # pass
        else:
            file_h5ad = flst[0]
            file = extract_path + '/%s' % file_h5ad
            if os.path.isfile(file):
                shutil.move(file, '.')
                print(f'File saved to: {file_h5ad}')
            elif os.path.isdir(file):
                flst2 = os.listdir(file)
                if len(flst2) > 1:
                    # shutil.move(file, '.')
                    for f in flst2:
                        ft = file + '/%s' % f
                        shutil.move(ft, '.')
                else:
                    file_h5ad = os.listdir(file)[0]
                    file = file + '/%s' % (file_h5ad)
                    shutil.move(file, '.')
                    print(f'File saved to: {file_h5ad}')
    
            shutil.rmtree(extract_path)
            if remove_org:
                os.remove(file_in)
            
        return file_h5ad
    except:
        return None


def load_sample_data_for_bi_practice( file_id = '1j-egYzjxhcz7xWwKXbgNMkzrh9q_W3Jp', out_path = 'BI_sample_dataset.tar.gz', remove_org = False ):
    download_from_google_drive( file_id, out_path = out_path, verbose = True )
    return decompress_tar_gz(out_path, remove_org = remove_org)


def load_from_gdrive( file_id = '1j-egYzjxhcz7xWwKXbgNMkzrh9q_W3Jp', file_type = 'tar.gz', remove_org = False ):
    download_from_google_drive( file_id, out_path = 'downloaded.%s' % file_type, verbose = True)
    if file_type == 'tar.gz':
        return decompress_tar_gz('downloaded.%s' % file_type, remove_org = remove_org)
    elif file_type == 'zip':
        return decompress_zip('downloaded.%s' % file_type, remove_zip = remove_org)
    elif file_type == 'gz':
        return decompress_gz('downloaded.%s' % file_type, remove_gz = remove_org)
    else:
        print( 'ERROR: file_type must be tar.gz, or zip, or gz.' )
        return None

