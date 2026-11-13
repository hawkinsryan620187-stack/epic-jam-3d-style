"""Run the local static-asset pipeline; no provider credentials are required."""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

def run(job_path, blender=None):
    job_path=Path(job_path).resolve()
    job=json.loads(job_path.read_text(encoding='utf-8'))
    for key in ('input','output'):
        p=Path(job[key]).expanduser()
        job[key]=str((job_path.parent/p).resolve() if not p.is_absolute() else p.resolve())
    src=Path(job['input']); out=Path(job['output'])
    if not src.is_file(): raise ValueError('Input file does not exist')
    if src.suffix.lower() not in ('.blend','.glb','.gltf','.fbx','.obj'):
        raise ValueError('An actual mesh is required. Image-to-3D is a preceding agent/tool stage.')
    if out.exists() and any(out.iterdir()): raise ValueError('Output must be new or empty; choose a new version folder')
    if out==src.parent or out in src.parents: raise ValueError('Output must not contain the source')
    executable=blender or os.environ.get('BLENDER_BIN') or shutil.which('blender')
    if not executable:
        for p in ('/Applications/Blender.app/Contents/MacOS/Blender',):
            if Path(p).is_file(): executable=p; break
    if not executable: raise RuntimeError('Blender not found; pass --blender with its full executable path')
    out.mkdir(parents=True,exist_ok=True)
    resolved=out/'resolved-job.json'; resolved.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
    script=Path(__file__).with_name('prepare_asset.py')
    with (out/'pipeline.log').open('w',encoding='utf-8') as log:
        result=subprocess.run([str(executable),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(script),'--',str(resolved)],stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError('Pipeline failed; inspect '+str(out/'pipeline.log'))
    report=json.loads((out/'asset-manifest.json').read_text(encoding='utf-8'))
    if report['export_roundtrip']!='passed': raise RuntimeError('Export verification did not pass')
    shutil.copy2(Path(__file__).with_name('ue_import.py'),out/'ue_import.py')
    print(json.dumps({'output':str(out),'export_roundtrip':report['export_roundtrip'],'visual_review':report['visual_review'],'ue_import':report['ue_import']},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job',required=True); parser.add_argument('--blender')
    args=parser.parse_args()
    try: run(args.job,args.blender)
    except (ValueError,RuntimeError,KeyError) as e:
        print(str(e),file=sys.stderr); sys.exit(1)
