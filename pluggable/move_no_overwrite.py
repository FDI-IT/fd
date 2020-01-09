import os

def move_no_overwrite(src, dst):
    """Attempts a safe move from src to dst. dst can be a full path or 
    directory. Will not overwrite existing files. Uses a renaming scheme 
    where an index is appended to the name to avoid naming conflicts.
    
    Returns the actual dst path.
    """
    src_basename = os.path.basename(src)
    src_head, src_tail = os.path.splitext(src_basename)
    
    if os.path.isdir(dst):
        dst_dir = dst
        dst_head = src_head
        dst_tail = src_tail
    else:
        dst_dir, dst_basename = os.path.split(dst)
        dst_head, dst_tail = os.path.splitext(dst_basename)
        
    count = 0
    while os.path.exists(dst):
        count += 1
        dst = os.path.join(dst_dir, "%s-%d%s" % (dst_head, count, dst_tail))
       
    os.rename(src, dst)
    return dst 
    