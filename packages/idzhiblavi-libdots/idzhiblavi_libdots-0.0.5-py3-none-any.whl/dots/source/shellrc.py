from loguru import logger

from dots.operation.write_file import WriteFile


class Shellrc:
    def __init__(self):
        self._env = {}
        self._aliases = {}
        self._path = []
        self._pre = []
        self._mid = []
        self._post = []

    def write_to(self, path: str):
        return WriteFile(
            content=self._render(),
            path=path,
        )

    def add_path(self, path: str):
        self._path.append(path)
        return self

    def add_env(self, key: str, value: str):
        if key in self._env and value != self._env[key]:
            logger.warning(
                f'overriding environment variable {key}="{self._env[key]}" with {value}',
            )

        self._env[key] = value
        return self

    def add_alias(self, key: str, value: str):
        if key in self._aliases and value != self._aliases[key]:
            logger.warning(
                f'overriding alias variable {key}="{self._aliases[key]}" with {value}',
            )

        self._aliases[key] = value
        return self

    def add_pre(self, code: str):
        self._pre.append(code)
        return self

    def add_mid(self, code: str):
        self._mid.append(code)
        return self

    def add_post(self, code: str):
        self._post.append(code)
        return self

    def _render(self) -> str:
        lines = []

        lines.extend(self._pre)
        self._render_environ(lines)
        self._render_path(lines)
        lines.extend(self._mid)
        self._render_aliases(lines)
        lines.extend(self._post)

        return "\n".join(lines)

    def _render_path(self, out: [str]):
        if not self._path:
            return
        path_env = ""
        for path in self._path:
            path_env += ":" + path
        out.append(f"export PATH={path_env}:${{PATH}}")

    def _render_environ(self, out: [str]):
        self._render_dict(self._env, "export", out)

    def _render_aliases(self, out: [str]):
        self._render_dict(self._aliases, "alias", out)

    def _render_dict(self, kv, prefix: str, out: [str]):
        for key, value in kv.items():
            out.append(f'{prefix} {key}="{str(value)}"')
