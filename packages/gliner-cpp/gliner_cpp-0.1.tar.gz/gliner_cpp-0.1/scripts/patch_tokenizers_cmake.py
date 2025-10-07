#!/usr/bin/env python3
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "deps/tokenizers-cpp/msgpack/CMakeLists.txt",
    ROOT / "deps/tokenizers-cpp/msgpack/test-install/CMakeLists.txt",
    ROOT / "deps/tokenizers-cpp/sentencepiece/CMakeLists.txt",
]
PATTERN = re.compile(
    r"(?i)(cmake_minimum_required\s*\(\s*VERSION\s+)([0-9][0-9.]*)([^)]*\))"
)
TARGET_VERSION = "3.18"
RUST_TARGET = ROOT / "deps/tokenizers-cpp/rust/src/lib.rs"
RUST_SNIPPETS = [
    (
        """    unsafe {\n        *out_cstr = (*handle).decode_str.as_mut_ptr();\n        *out_len = (*handle).decode_str.len();\n    }\n""",
        """    unsafe {\n        let wrapper = &mut *handle;\n        let decode_len = wrapper.decode_str.len();\n        *out_len = decode_len;\n        *out_cstr = wrapper.decode_str.as_mut_ptr();\n    }\n""",
    ),
    (
        """    unsafe {\n        let str = (*handle).tokenizer.id_to_token(id);\n        (*handle).id_to_token_result = match str {\n            Some(s) => s,\n            None => String::from(\"\"),\n        };\n\n        *out_cstr = (*handle).id_to_token_result.as_mut_ptr();\n        *out_len = (*handle).id_to_token_result.len();\n    }\n""",
        """    unsafe {\n        let wrapper = &mut *handle;\n        let str = wrapper.tokenizer.id_to_token(id);\n        wrapper.id_to_token_result = match str {\n            Some(s) => s,\n            None => String::from(\"\"),\n        };\n\n        let token_len = wrapper.id_to_token_result.len();\n        *out_len = token_len;\n        *out_cstr = wrapper.id_to_token_result.as_mut_ptr();\n    }\n""",
    ),
]


def needs_update(version: str) -> bool:
    def parse(v: str) -> list[int]:
        return [int(p) for p in v.split(".") if p]

    current_parts = parse(version)
    target_parts = parse(TARGET_VERSION)
    length = max(len(current_parts), len(target_parts))
    current_parts += [0] * (length - len(current_parts))
    target_parts += [0] * (length - len(target_parts))
    return current_parts < target_parts


def make_replacer():
    state = {"updated": 0}
    seen_versions: list[str] = []

    def replacer(match: re.Match[str]) -> str:
        prefix, version, suffix = match.groups()
        seen_versions.append(version)
        if needs_update(version):
            state["updated"] += 1
            return f"{prefix}{TARGET_VERSION}{suffix}"
        return match.group(0)

    return PATTERN, replacer, state, seen_versions


def patch(path: pathlib.Path) -> int:
    if not path.exists():
        print(f"{path}: file not found")
        return 0
    text = path.read_text()
    pattern, replacer, state, seen_versions = make_replacer()
    new_text, _ = pattern.subn(replacer, text)
    if seen_versions:
        if state["updated"]:
            print(f"{path}: updated {state['updated']} occurrence(s) (found versions: {', '.join(seen_versions)})")
        else:
            print(f"{path}: already >= {TARGET_VERSION} (found versions: {', '.join(seen_versions)})")
    else:
        print(f"{path}: no cmake_minimum_required directive found")
    if state["updated"]:
        path.write_text(new_text)
    return state["updated"]


def patch_rust(path: pathlib.Path) -> int:
    if not path.exists():
        print(f"{path}: file not found")
        return 0

    text = path.read_text()

    if "let wrapper = &mut *handle;" in text:
        print(f"{path}: pointer fixes already present.")
        return 0

    for original, _ in RUST_SNIPPETS:
        if original not in text:
            print(f"{path}: expected snippet not found; skipping pointer fix.")
            return 0

    new_text = text
    for original, replacement in RUST_SNIPPETS:
        new_text = new_text.replace(original, replacement, 1)

    if new_text != text:
        path.write_text(new_text)
        return len(RUST_SNIPPETS)

    return 0


def main() -> int:
    cmake_updates = 0
    for target in TARGETS:
        cmake_updates += patch(target)
    if cmake_updates == 0:
        print("No cmake_minimum_required directives updated.")
    else:
        print(f"Updated cmake_minimum_required in {cmake_updates} location(s).")

    rust_updates = patch_rust(RUST_TARGET)
    if rust_updates > 0:
        print(f"Patched tokenizers rust bindings in {rust_updates} block(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
