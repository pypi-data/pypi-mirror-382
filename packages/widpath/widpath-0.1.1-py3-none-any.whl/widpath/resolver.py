from pathlib import Path

class WidPathResolver:
    def __init__(self, root='.',  size: int = 2, separator: str = "/"):
        assert(size>0)
        self.size = size
        self.separator = separator
        self.root=Path(root)

    def _split_wid(self, wid: str):
        return [wid[i:i + self.size] for i in range(0, len(wid), self.size)]

    def get_max_level(self, wid: str) -> int:
        return len(wid) // self.size - 1

    def get_hierarchical_json(self, wid: str, level: int) -> Path:
        parts = self._split_wid(wid)
        max_level = self.get_max_level(wid)
        level = min(max(level, 0), max_level)
        if level >= max_level:
            return self.root / Path(self.separator.join(parts[:max_level+1]) + ".json")
        else:
            return self.root / Path(self.separator.join(parts[:level+1]) + ".json")

    def get_file_path(self, wid: str) -> Path:
        min_level = 0
        max_level = self.get_max_level(wid)
        level = max_level

        while True:
            cur_file = self.get_hierarchical_json(wid, level)
            if cur_file.exists():
                return cur_file
            if not cur_file.parent.exists():
                if level == min_level:
                    return cur_file
                max_level = level
                level = (level + min_level) // 2
            else:
                next_file = self.get_hierarchical_json(wid, level+1)
                if next_file != cur_file and next_file.parent.exists():
                    min_level = level
                    level = (level + max_level) // 2
                else:
                    return cur_file
