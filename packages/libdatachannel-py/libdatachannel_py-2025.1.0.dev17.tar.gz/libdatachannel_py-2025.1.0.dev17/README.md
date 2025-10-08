# libdatachannel-py

[![PyPI](https://img.shields.io/pypi/v/libdatachannel-py)](https://pypi.org/project/libdatachannel-py/)
[![image](https://img.shields.io/pypi/pyversions/libdatachannel-py.svg)](https://pypi.python.org/pypi/libdatachannel-py)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Actions status](https://github.com/shiguredo/libdatachannel-py/workflows/build/badge.svg)](https://github.com/shiguredo/sora-python-sdk/actions)

## About Shiguredo's open source software

We will not respond to PRs or issues that have not been discussed on Discord. Also, Discord is only available in Japanese.

Please read <https://github.com/shiguredo/oss/blob/master/README.en.md> before use.

## 時雨堂のオープンソースソフトウェアについて

利用前に <https://github.com/shiguredo/oss> をお読みください。

## libdatachannel-py について

[libdatachannel](https://github.com/paullouisageneau/libdatachannel) の Python バインディングです。

## 特徴

- [nanobind](https://github.com/wjakob/nanobind) を利用しています
- [Opus](https://opus-codec.org/) を利用した Opus ソフトウェアエンコード/デコードに対応しています
- [libaom](https://aomedia.googlesource.com/aom/) を利用した AV1 ソフトウェアエンコード/デコードに対応しています
- [OpenH264](https://www.openh264.org/) を利用した H.264 ソフトウェアエンコード/デコードに対応しています
- [Apple Video Toolbox](https://developer.apple.com/documentation/videotoolbox) を利用した H.264/H.265 ハードウェアエンコード/デコードに対応しています

## 優先実装

優先実装とは Sora / Sora Cloud の契約頂いているお客様向けに libdatachannel-py の実装予定機能を有償にて前倒しで実装することです。

**詳細は Discord やメールなどでお気軽にお問い合わせください**

### 優先実装が可能な機能一覧

- Ubuntu 22.04 対応
  - x86_64
  - arm64
- macOS 14 対応
  - arm64
- Windows 11 対応
  - x86_64
  - arm64
- Windows Server 2025 対応
  - x86_64
  - arm64
- Python 3.12 対応
- Python 3.11 対応

## サポートについて

### Discord

- **サポートしません**
- アドバイスします
- フィードバック歓迎します

最新の状況などは Discord で共有しています。質問や相談も Discord でのみ受け付けています。

<https://discord.gg/shiguredo>

### バグ報告

Discord へお願いします。

## ライセンス

Apache License 2.0

```text
Copyright 2025-2025, Wandbox LLC (Original Author)
Copyright 2025-2025, Shiguredo Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## OpenH264

<https://www.openh264.org/BINARY_LICENSE.txt>

```text
"OpenH264 Video Codec provided by Cisco Systems, Inc."
```
