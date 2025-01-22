# [1.1.0-dev.1](https://github.com/Francesco146/telegram-file-statistics-bot/compare/v1.0.0...v1.1.0-dev.1) (2025-01-22)


### Bug Fixes

* handle missing file name or size ([4d8661a](https://github.com/Francesco146/telegram-file-statistics-bot/commit/4d8661a15e09a4813a2641008441e8d27dc3053f))
* inline keyboard was shown even on error ([4c22709](https://github.com/Francesco146/telegram-file-statistics-bot/commit/4c22709232c157cd022d8b3fc06af34b61f02d63))
* log a warning for unsupported languages ([fc9bc8e](https://github.com/Francesco146/telegram-file-statistics-bot/commit/fc9bc8e4317d0f0ee155916096134d763efedbfd))
* send function not properly initialized ([a9d8bb0](https://github.com/Francesco146/telegram-file-statistics-bot/commit/a9d8bb05bb9fe497fbc71990b9d4c860f09c23da))
* set default fixture loop scope for asyncio in pytest configuration ([140efbf](https://github.com/Francesco146/telegram-file-statistics-bot/commit/140efbf95992ed287ec1184ba2c20e0516595f75))
* update Italian localization file with bug report link and language tag ([e0d03a9](https://github.com/Francesco146/telegram-file-statistics-bot/commit/e0d03a92ccafc3e25e60008e2c0086feacfc20cb))
* update test cases to use mocked get_str instead of logger ([66b3c40](https://github.com/Francesco146/telegram-file-statistics-bot/commit/66b3c4012f948ac1d099a0e4616f9936483c229e))
* validate file name and size before processing ([0b3f51d](https://github.com/Francesco146/telegram-file-statistics-bot/commit/0b3f51d175584e2866db308f2295546303f576c5))


### Features

* add Docker support ([e5d5b02](https://github.com/Francesco146/telegram-file-statistics-bot/commit/e5d5b02032489c6b6f7ce279879bf411ca0881ac))
* add Makefile for localization management and build targets ([92266f6](https://github.com/Francesco146/telegram-file-statistics-bot/commit/92266f6860d55ad4c3b0976ab7488cbc564cd1c4))
* add module docstrings and refactor database singleton ([25ae4b7](https://github.com/Francesco146/telegram-file-statistics-bot/commit/25ae4b7043040331cc12ea0ceb5ea0de44d463c2))
* add pluralization support using `ngettext` ([8184b6a](https://github.com/Francesco146/telegram-file-statistics-bot/commit/8184b6a68cddb862eb7bb89cd63ecae327c3b004))
* drop support of older Python versions ([18d6d98](https://github.com/Francesco146/telegram-file-statistics-bot/commit/18d6d98d4c4e59fd3503ded6855a0ff19eaa77ad))
* enhance error handling based on pyright ([f763ec1](https://github.com/Francesco146/telegram-file-statistics-bot/commit/f763ec17e94438d048091db1512c7b5fe7057d72))
* lint for compliance of PEP8 ([1ef82d3](https://github.com/Francesco146/telegram-file-statistics-bot/commit/1ef82d3dd5a4c0db1aa2b19ab80619ed104fbf25))
* show reset button only if the user has valid statistics ([9a60ab8](https://github.com/Francesco146/telegram-file-statistics-bot/commit/9a60ab8d7813c66be06ba6e0b63168c73fe308e0))
* support env configuration ([eb348b0](https://github.com/Francesco146/telegram-file-statistics-bot/commit/eb348b06766b5bc32a785a0a132f9c6940cd533e))
* update backend structure for PEP621 compliance ([100fc54](https://github.com/Francesco146/telegram-file-statistics-bot/commit/100fc54dcd2572203b161d75ff27be218ff51e4a))
* use semantic-release ([d6e6c6a](https://github.com/Francesco146/telegram-file-statistics-bot/commit/d6e6c6aed59001ed1bc5eff400251ff9af7658d6))