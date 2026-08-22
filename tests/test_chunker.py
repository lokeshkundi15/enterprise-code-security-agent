from app.core.chunker import filter_and_chunk_diff

def test_filter_ignores_lockfiles():
    files = [
        {"file_path": "package-lock.json", "changes": '{"name": "test"}'},
        {"file_path": "src/app.py", "changes": "print('hello')"}
    ]
    filtered = filter_and_chunk_diff(files)
    assert len(filtered) == 1
    assert filtered[0]["file_path"] == "src/app.py"

def test_diff_truncation_limits_context():
    large_changes = "\n".join([f"+line {i} = {i}" for i in range(500)])
    files = [{"file_path": "src/big_file.py", "changes": large_changes}]
    
    processed = filter_and_chunk_diff(files)
    assert processed[0]["is_truncated"] is True
    assert len(processed[0]["changes"].splitlines()) <= 260