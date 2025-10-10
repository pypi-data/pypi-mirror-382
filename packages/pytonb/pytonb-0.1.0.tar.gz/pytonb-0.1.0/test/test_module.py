from pytonb import write_notebook, write_script, sync, sync_folder
import json, io, time, contextlib


def test_write_notebook():
    return_cells=False
    use_ast=True
    src='data/test-notebook_orig.py'
    dst='data/test-notebook_mod.ipynb'
    cmp='data/test-notebook_orig.ipynb'
    j=write_notebook(src,save_name=dst)
    with open(cmp)as f:
        c1=json.load(f)
    with open(dst)as f:
        c2=json.load(f)
    ca=[c['source'] for c in c1['cells']]
    cb=[c['source'] for c in c2['cells']]
    assert len(ca)==len(cb)
    assert ca==cb


def test_write_script():
    src='data/test-notebook_orig.ipynb'
    dst='data/test-notebook_mod.py'
    cmp='data/test-notebook_orig.py'
    j=write_script(src,save_name=dst)
    with open(cmp)as f:
        c1=f.read()
    with open(dst)as f:
        c2=f.read()
    assert c1 == c2


def test_sync():
    b = io.StringIO()
    delay=0.2
    with contextlib.redirect_stdout(b):
        # non-extistent file
        p='non_existent_dir/non_existent_file.ipynb'
        e=sync( p, delay=delay, vb=2)
        assert e is None
        assert b.getvalue()==f'not a file: {p}\n'
        b.truncate(0)
        b.seek(0)
        # existing file
        p='data/test-notebook_mod.ipynb'
        e=sync( p, delay=delay, vb=2)
        time.sleep(delay)
        assert b.getvalue()=='syncing data/test-notebook_mod.ipynb\n'
        b.truncate(0)
        b.seek(0)
        e.set()
        time.sleep(delay)
        assert b.getvalue()=='sync stopped for data/test-notebook_mod.ipynb\n'

def test_sync_folder():
    b = io.StringIO()
    exs=['data/test-notebook_mod.ipynb', 'data/test-notebook_orig.ipynb', ]
    delay=0.3
    with contextlib.redirect_stdout(b):
        p='non_existent_dir/non_existent_file.ipynb'
        e=sync_folder('.', recursion_level=2, vb=1)
        time.sleep(delay)
        for ex in exs:
            assert f'syncing {ex}' in b.getvalue()
        b.truncate(0)
        b.seek(0)
        e.set()
        time.sleep(delay*len(exs)*6)
        for ex in exs:
            assert f'sync stopped for {ex}' in b.getvalue()

def tests():
    test_write_notebook()
    test_write_script()
    test_sync()
    test_sync_folder()

