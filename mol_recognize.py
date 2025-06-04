import requests
import base64
import hashlib
import time
import random
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Union
from tqdm import tqdm


def img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_img2mol(api_base: str, img_path: Path) -> str:
    payload = {"base64_img": img_to_base64(img_path)}
    url = f"{api_base.rstrip('/')}/mol/img2mol"
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"img2mol failed for {img_path.name}: {data.get('msg')}")
    return data["data"]


def call_draw_mol(api_base: str, smiles: str) -> bytes:
    url = f"{api_base.rstrip('/')}/mol/draw_mol"
    resp = requests.get(url, params={"mol": smiles}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"draw_mol failed for SMILES {smiles}: {data.get('msg')}")
    return base64.b64decode(data["data"])


def retry_with_backoff(func, retries=3, base_delay=1):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt < retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                raise e


def process_image_directory(image_dir: Union[str, Path], api_base: str = "") -> pd.DataFrame:
    image_dir = Path(image_dir)
    assert image_dir.exists() and image_dir.is_dir(), f"路径无效：{image_dir}"

    result_dir = image_dir.parent / "result"
    svg_dir = result_dir / "svg"
    result_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)

    result_csv_path = result_dir / "img2mol.csv"
    error_log_path = result_dir / "img2mol_error.log"
    error_log = open(error_log_path, "a", encoding="utf-8")

    existing_df = pd.read_csv(result_csv_path) if result_csv_path.exists() else pd.DataFrame()
    processed_hashes = set(existing_df["sha256"].tolist()) if "sha256" in existing_df.columns else set()

    records = []

    image_paths = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
    for img_path in tqdm(image_paths, desc="处理图片"):
        img_hash = compute_sha256(img_path)
        if img_hash in processed_hashes:
            print(f"跳过已处理：{img_path.name}")
            continue

        try:
            smiles = retry_with_backoff(lambda: call_img2mol(api_base, img_path))
            svg_bytes = retry_with_backoff(lambda: call_draw_mol(api_base, smiles))

            svg_name = img_path.stem + ".svg"
            svg_path = svg_dir / svg_name
            svg_path.write_bytes(svg_bytes)

            record = {
                "image_path": str(img_path.resolve()),
                "sha256": img_hash,
                "smiles": smiles,
                "svg_path": str(svg_path.resolve()),
                "created_at": datetime.now().isoformat(timespec='seconds')
            }
            records.append(record)

            time.sleep(random.uniform(1, 3))  # 模拟人类行为
        except Exception as e:
            msg = f"{datetime.now().isoformat()} 处理失败: {img_path.name} - {repr(e)}\n"
            print(msg.strip())
            error_log.write(msg)
            error_log.flush()
            continue

    error_log.close()

    new_df = pd.DataFrame(records)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(result_csv_path, index=False, encoding="utf-8-sig")

    print(f"\n处理完成 ✅ 共新增 {len(new_df)} 张，结果已保存至：{result_csv_path}")
    print(f"失败记录保存在：{error_log_path}")
    return combined_df

if __name__ == "__main__":
    df = process_image_directory("./imgs")
    print(df.head())
