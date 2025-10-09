# Changelog

## 0.2.0 (2025-10-08)

Full Changelog: [v0.1.1...v0.2.0](https://github.com/straddleio/straddle-python/compare/v0.1.1...v0.2.0)

### Features

* **api:** manual updates ([ed0226f](https://github.com/straddleio/straddle-python/commit/ed0226fa8e3de4720587a59ad50bc81db2db0d9c))
* **api:** manual updates ([63beb58](https://github.com/straddleio/straddle-python/commit/63beb586c9aa10325832a9612e3256e591092342))
* clean up environment call outs ([1eeb12e](https://github.com/straddleio/straddle-python/commit/1eeb12ee7967b2f88259243676d1da7af4578448))
* **client:** support file upload requests ([e448cbf](https://github.com/straddleio/straddle-python/commit/e448cbf159492da146af602ba6c93cea9cbbd127))
* **docs:** Preliminary update to SDK Spec ([4804262](https://github.com/straddleio/straddle-python/commit/48042621b00122c58d546bb10c193c4604710d4e))
* **docs:** Preliminary update to SDK Spec ([e05ec17](https://github.com/straddleio/straddle-python/commit/e05ec179f2090a26fd0464510064498f48fddc89))
* **docs:** Preliminary update to SDK Spec ([cbcf851](https://github.com/straddleio/straddle-python/commit/cbcf851be1c53e057a1bf366fa4ae64236af2e57))
* **docs:** Preliminary update to SDK Spec ([7de8480](https://github.com/straddleio/straddle-python/commit/7de8480be3a183a06ab97655f93918fbb0f2e0cc))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([ef1c61b](https://github.com/straddleio/straddle-python/commit/ef1c61b0e920bbf926f7516538118a07137703cb))
* improve future compat with pydantic v3 ([76e3d9c](https://github.com/straddleio/straddle-python/commit/76e3d9c8d50b578f8eba58ac7e7982628a4d844f))
* **types:** replace List[str] with SequenceNotStr in params ([6bec736](https://github.com/straddleio/straddle-python/commit/6bec736fac137477ad58c8f091ea0d5524b0a4a9))


### Bug Fixes

* **api:** update default API URLs and metadata ([3906af1](https://github.com/straddleio/straddle-python/commit/3906af12af19753d0f2afcbbb57532322d9522ea))
* avoid newer type syntax ([a266c71](https://github.com/straddleio/straddle-python/commit/a266c718d4ea4ead0882317480006c9fb27749b1))
* **client:** don't send Content-Type header on GET requests ([920023c](https://github.com/straddleio/straddle-python/commit/920023c5b45971ded364ecafc21083ef072a3f64))
* **parsing:** correctly handle nested discriminated unions ([322d631](https://github.com/straddleio/straddle-python/commit/322d63189df7b02b6083fca47a0693cc1359a1cd))
* **parsing:** ignore empty metadata ([22359b1](https://github.com/straddleio/straddle-python/commit/22359b1cc4dff65d06dcfd67193a123dc366972a))
* **parsing:** parse extra field types ([8f4d0b3](https://github.com/straddleio/straddle-python/commit/8f4d0b3b518ea8dd84ac9d74695a159b539cad6b))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([81890ea](https://github.com/straddleio/straddle-python/commit/81890ea2aece552115aac1bcfab5af76e4d7ef55))
* **internal:** add Sequence related utils ([5395eb9](https://github.com/straddleio/straddle-python/commit/5395eb9ff14db0c96040c203cb4ca758a04e089d))
* **internal:** bump pinned h11 dep ([9e8ed7b](https://github.com/straddleio/straddle-python/commit/9e8ed7bff3b943e492ed05cad384a80e7d5b241e))
* **internal:** change ci workflow machines ([b4bb048](https://github.com/straddleio/straddle-python/commit/b4bb0489b3f2812c008664a6ed29dfe528760c3c))
* **internal:** fix ruff target version ([8fdd795](https://github.com/straddleio/straddle-python/commit/8fdd795e9fdcfd4826a89e835e4d49a4eee9f0fb))
* **internal:** move mypy configurations to `pyproject.toml` file ([0b44b5a](https://github.com/straddleio/straddle-python/commit/0b44b5aeb48329cbbffb256ca2b5ab8b9fce804b))
* **internal:** update comment in script ([ae5935d](https://github.com/straddleio/straddle-python/commit/ae5935d0d934e5fd261ccd15b8539f4ac506d78a))
* **internal:** update pydantic dependency ([e7389fc](https://github.com/straddleio/straddle-python/commit/e7389fce80db21c6b4f7109d8bcbe2d0dc251ac1))
* **internal:** update pyright exclude list ([062e369](https://github.com/straddleio/straddle-python/commit/062e3694e0e8e39ab45f80b048cc62e294d719b6))
* **package:** mark python 3.13 as supported ([0600578](https://github.com/straddleio/straddle-python/commit/060057822f8c438b09c70edb8ba345f7faec7ef4))
* **project:** add settings file for vscode ([5a68c73](https://github.com/straddleio/straddle-python/commit/5a68c737bc232b4491d5c4865f648f68fa9befcf))
* **readme:** fix version rendering on pypi ([700785d](https://github.com/straddleio/straddle-python/commit/700785dfc4d079c5ee36387013a6f65e7633fe68))
* **tests:** simplify `get_platform` test ([ad59931](https://github.com/straddleio/straddle-python/commit/ad599311e35f46ebbc775c669ef2f9e8a1474d2d))
* **types:** change optional parameter type from NotGiven to Omit ([263a72c](https://github.com/straddleio/straddle-python/commit/263a72c33d46c0314a7491068a76915406e518a7))
* update @stainless-api/prism-cli to v5.15.0 ([c5aa610](https://github.com/straddleio/straddle-python/commit/c5aa610509a4e64b4d12a9218d9b852a3735b38c))
* update github action ([d02ccd1](https://github.com/straddleio/straddle-python/commit/d02ccd151c4b857ce88a64b735995d62f3c36720))

## 0.1.1 (2025-07-08)

Full Changelog: [v0.1.0...v0.1.1](https://github.com/straddleio/straddle-python/compare/v0.1.0...v0.1.1)

### Features

* **api:** fix tests ([#72](https://github.com/straddleio/straddle-python/issues/72)) ([d7a97f2](https://github.com/straddleio/straddle-python/commit/d7a97f298dfc950792b520d8a54d86156d1b5138))
* **api:** manual updates ([79c6816](https://github.com/straddleio/straddle-python/commit/79c68168f90578a9c345994de1b9a2fd5b62ae24))
* **api:** manual updates ([b993e78](https://github.com/straddleio/straddle-python/commit/b993e7816ba57de14fa40dbbe445578ac843a23e))
* **api:** manual updates ([#48](https://github.com/straddleio/straddle-python/issues/48)) ([e8fe9fd](https://github.com/straddleio/straddle-python/commit/e8fe9fd2f4b0a8b5115badc04068c07607ecba01))
* **api:** manual updates ([#66](https://github.com/straddleio/straddle-python/issues/66)) ([47515b4](https://github.com/straddleio/straddle-python/commit/47515b4ff80549cedee474dbe2724094554a195b))
* **api:** Remove explicit environment setting ([33baffb](https://github.com/straddleio/straddle-python/commit/33baffbd3e0bf805607f82ef7cc7f6e6f3b1de50))
* **client:** add follow_redirects request option ([4081f8e](https://github.com/straddleio/straddle-python/commit/4081f8efd0c55f780f05c585ce27bc4305d6ab95))
* **client:** add support for aiohttp ([95a4be8](https://github.com/straddleio/straddle-python/commit/95a4be8bf40021723c103cd029cf21c708b2a7a1))
* **client:** allow passing `NotGiven` for body ([#41](https://github.com/straddleio/straddle-python/issues/41)) ([11a1bf8](https://github.com/straddleio/straddle-python/commit/11a1bf8761cda12b62fe15ae46fbfc30cb9a17f3))
* **client:** send `X-Stainless-Read-Timeout` header ([#34](https://github.com/straddleio/straddle-python/issues/34)) ([1807309](https://github.com/straddleio/straddle-python/commit/1807309e0c50315a440b594e7ed7fab297820b54))
* **docs:** Preliminary update to SDK Spec ([9c10eb9](https://github.com/straddleio/straddle-python/commit/9c10eb9b9a7f2c96945f3c58791a4ac2a77b7b7b))
* **docs:** Preliminary update to SDK Spec ([#29](https://github.com/straddleio/straddle-python/issues/29)) ([8c78fe5](https://github.com/straddleio/straddle-python/commit/8c78fe51f7b41727996c3b2a86fcfa9f880496a7))
* **docs:** Preliminary update to SDK Spec ([#37](https://github.com/straddleio/straddle-python/issues/37)) ([462d501](https://github.com/straddleio/straddle-python/commit/462d5018b18fd881c5eccb9487150b750abe58d8))
* **docs:** Preliminary update to SDK Spec ([#65](https://github.com/straddleio/straddle-python/issues/65)) ([df99707](https://github.com/straddleio/straddle-python/commit/df99707c9eaec7a8c590d4a2cbd359dc825cf439))
* **docs:** Preliminary update to SDK Spec ([#67](https://github.com/straddleio/straddle-python/issues/67)) ([4a2e3e5](https://github.com/straddleio/straddle-python/commit/4a2e3e59ecc7d7d3c8b2753c626b67461b146fb9))
* **docs:** Preliminary update to SDK Spec ([#69](https://github.com/straddleio/straddle-python/issues/69)) ([791d28c](https://github.com/straddleio/straddle-python/commit/791d28c945d8d24be2275c1b1c360585f70dee40))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#33](https://github.com/straddleio/straddle-python/issues/33)) ([56264ac](https://github.com/straddleio/straddle-python/commit/56264ac2753163991f9009f1c0c4b378a25a85bb))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#40](https://github.com/straddleio/straddle-python/issues/40)) ([b7f18a1](https://github.com/straddleio/straddle-python/commit/b7f18a1eb6ec4421f8c4c8014605826e19e66f02))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#47](https://github.com/straddleio/straddle-python/issues/47)) ([4012a22](https://github.com/straddleio/straddle-python/commit/4012a2267d853a38034f9a66f42585e438d96b0d))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#52](https://github.com/straddleio/straddle-python/issues/52)) ([4be4b9f](https://github.com/straddleio/straddle-python/commit/4be4b9f9577065034ff676297c29383d15f6fc7c))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#53](https://github.com/straddleio/straddle-python/issues/53)) ([6c3006b](https://github.com/straddleio/straddle-python/commit/6c3006b577f34b0df78b01e577870e669857adbc))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#58](https://github.com/straddleio/straddle-python/issues/58)) ([e4c0685](https://github.com/straddleio/straddle-python/commit/e4c06858e4933015ea4e58b7b637775d45edd2f1))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#59](https://github.com/straddleio/straddle-python/issues/59)) ([ab7df02](https://github.com/straddleio/straddle-python/commit/ab7df02baf0ecaff85da191b9d9f3cccfe242b80))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#60](https://github.com/straddleio/straddle-python/issues/60)) ([8ada0ae](https://github.com/straddleio/straddle-python/commit/8ada0ae6ea7fdaf9d0ef396af016de31c2e7395e))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#61](https://github.com/straddleio/straddle-python/issues/61)) ([ad1bba6](https://github.com/straddleio/straddle-python/commit/ad1bba6066cc1961d8737192302d154b56062d3b))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#62](https://github.com/straddleio/straddle-python/issues/62)) ([d9ffe23](https://github.com/straddleio/straddle-python/commit/d9ffe23bfdf49d087a61e12217e0fad60b5ef8aa))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#63](https://github.com/straddleio/straddle-python/issues/63)) ([3a66dec](https://github.com/straddleio/straddle-python/commit/3a66dece8ca31dd31d5a04250f40945ad74d018a))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#68](https://github.com/straddleio/straddle-python/issues/68)) ([68ee711](https://github.com/straddleio/straddle-python/commit/68ee7112dca1514f863f6721341501e88250c379))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#70](https://github.com/straddleio/straddle-python/issues/70)) ([7ab2a78](https://github.com/straddleio/straddle-python/commit/7ab2a78ac6f6cf27a2dc49365f9779ecc3821ade))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#71](https://github.com/straddleio/straddle-python/issues/71)) ([d73c517](https://github.com/straddleio/straddle-python/commit/d73c517bdd4ac5c260b201161fd2cd38c1d9419c))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#39](https://github.com/straddleio/straddle-python/issues/39)) ([b441fc4](https://github.com/straddleio/straddle-python/commit/b441fc4e7923f002d02640d8478ada2c57a93f06))
* **ci:** correct conditional ([63de43d](https://github.com/straddleio/straddle-python/commit/63de43d58ca23044142c6992514e4430b9e7a201))
* **ci:** ensure pip is always available ([#56](https://github.com/straddleio/straddle-python/issues/56)) ([122978a](https://github.com/straddleio/straddle-python/commit/122978af5964ddfa727b2b5db97a3ad8f031e256))
* **ci:** release-doctor — report correct token name ([d821d19](https://github.com/straddleio/straddle-python/commit/d821d19713ee19d597e4682db84520c178789e94))
* **ci:** remove publishing patch ([#57](https://github.com/straddleio/straddle-python/issues/57)) ([6675e88](https://github.com/straddleio/straddle-python/commit/6675e88071773d4609667fa8fe5070521e5d31e5))
* **client:** correctly parse binary response | stream ([8bf8f1a](https://github.com/straddleio/straddle-python/commit/8bf8f1a411b7430acfc024043e790fb2aacebcba))
* **client:** mark some request bodies as optional ([11a1bf8](https://github.com/straddleio/straddle-python/commit/11a1bf8761cda12b62fe15ae46fbfc30cb9a17f3))
* **package:** support direct resource imports ([6bbe896](https://github.com/straddleio/straddle-python/commit/6bbe8963465b03a8f6c26b79b4bd951b35a0a495))
* **pydantic v1:** more robust ModelField.annotation check ([ec686b7](https://github.com/straddleio/straddle-python/commit/ec686b79743595f916a8848f076d5f20f3593811))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([d563fd4](https://github.com/straddleio/straddle-python/commit/d563fd458b9af2ad0314278f7503f480805a980a))
* **types:** handle more discriminated union shapes ([#55](https://github.com/straddleio/straddle-python/issues/55)) ([1db115f](https://github.com/straddleio/straddle-python/commit/1db115f48d8ebb5c672e9cae12952f19b5f75e6c))


### Chores

* **ci:** add timeout thresholds for CI jobs ([168aab2](https://github.com/straddleio/straddle-python/commit/168aab2a05f968457add55bd62b55299f202f553))
* **ci:** change upload type ([d031781](https://github.com/straddleio/straddle-python/commit/d0317811ae6e7afd4645cd6b72a13d65a9c47704))
* **ci:** enable for pull requests ([f42a525](https://github.com/straddleio/straddle-python/commit/f42a52560920862cbb3e2bb8fc80e53fe9d53378))
* **ci:** fix installation instructions ([fa77e84](https://github.com/straddleio/straddle-python/commit/fa77e84f4ef34604fd2e1d10dfef5b46edf35478))
* **ci:** only run for pushes and fork pull requests ([5751c31](https://github.com/straddleio/straddle-python/commit/5751c318b917ef1b1c1cd86bd94c323358695fbb))
* **ci:** upload sdks to package manager ([9398ccc](https://github.com/straddleio/straddle-python/commit/9398ccc86ca16faba4e6aa025d8e246b359ce658))
* **client:** minor internal fixes ([9a8707e](https://github.com/straddleio/straddle-python/commit/9a8707ec9ecbf5aef48cd892d3de8d96e217a717))
* codegen updates ([6dde262](https://github.com/straddleio/straddle-python/commit/6dde262e331211991723ca73bb156dbe8f888e48))
* **docs:** grammar improvements ([423b56a](https://github.com/straddleio/straddle-python/commit/423b56a28e9c4f97e410fc4a02ac262297b836cd))
* **docs:** remove reference to rye shell ([fe3cca4](https://github.com/straddleio/straddle-python/commit/fe3cca413e9e5c028df0d72de04098ccab4d3dad))
* **docs:** update client docstring ([#45](https://github.com/straddleio/straddle-python/issues/45)) ([ecd7279](https://github.com/straddleio/straddle-python/commit/ecd7279da62cc1d59ff5c035dbb3276efc8276da))
* fix typos ([#64](https://github.com/straddleio/straddle-python/issues/64)) ([c44a22b](https://github.com/straddleio/straddle-python/commit/c44a22b129d2297ef5dceec1b0997abcdcaddca0))
* **internal:** avoid errors for isinstance checks on proxies ([0281899](https://github.com/straddleio/straddle-python/commit/0281899ebead6c0e67a2003aafcbb99ce97eb96b))
* **internal:** base client updates ([82b768b](https://github.com/straddleio/straddle-python/commit/82b768bf4cf563fb0fab2e5b3c4acaf5c762d144))
* **internal:** bummp ruff dependency ([#32](https://github.com/straddleio/straddle-python/issues/32)) ([adec2d0](https://github.com/straddleio/straddle-python/commit/adec2d031a0697202040871f94b44295d9fc62d0))
* **internal:** bump pyright version ([a0168ad](https://github.com/straddleio/straddle-python/commit/a0168adef7c0d558c975303c19d2fb689420e7d8))
* **internal:** bump rye to 0.44.0 ([#54](https://github.com/straddleio/straddle-python/issues/54)) ([6eb5bea](https://github.com/straddleio/straddle-python/commit/6eb5beaaf0a062e4949b1ad95002fda54e380b2a))
* **internal:** change default timeout to an int ([#31](https://github.com/straddleio/straddle-python/issues/31)) ([8dc087a](https://github.com/straddleio/straddle-python/commit/8dc087a24d069cffde2d431cdc5a539098589359))
* **internal:** codegen related update ([c2073fb](https://github.com/straddleio/straddle-python/commit/c2073fb686a304869b8f024bbb3a43ad44026af0))
* **internal:** codegen related update ([7120d83](https://github.com/straddleio/straddle-python/commit/7120d83d2355f3c25372721788df850e90eba9a3))
* **internal:** codegen related update ([56a03c4](https://github.com/straddleio/straddle-python/commit/56a03c401aa1bf34f6ad2e6793944a8d91a92a1e))
* **internal:** fix devcontainers setup ([#42](https://github.com/straddleio/straddle-python/issues/42)) ([4e51cb7](https://github.com/straddleio/straddle-python/commit/4e51cb777e878494be88896fe2a3daf6863e7621))
* **internal:** fix list file params ([c86394e](https://github.com/straddleio/straddle-python/commit/c86394e87474ab815c79fe2ad0770783479a5725))
* **internal:** fix type traversing dictionary params ([#35](https://github.com/straddleio/straddle-python/issues/35)) ([56d6f4b](https://github.com/straddleio/straddle-python/commit/56d6f4b2d44f0278619b86bc4dfb5e5ec050ad10))
* **internal:** import reformatting ([37b1e5e](https://github.com/straddleio/straddle-python/commit/37b1e5e50bbe4d36765900128b3828da19bcc012))
* **internal:** minor type handling changes ([#36](https://github.com/straddleio/straddle-python/issues/36)) ([260b180](https://github.com/straddleio/straddle-python/commit/260b180be3b072af83c70a38b05a73a18f22c95b))
* **internal:** properly set __pydantic_private__ ([#43](https://github.com/straddleio/straddle-python/issues/43)) ([1c351b6](https://github.com/straddleio/straddle-python/commit/1c351b6e6f41a621b1351a431a00db86b82ba77a))
* **internal:** refactor retries to not use recursion ([4802673](https://github.com/straddleio/straddle-python/commit/480267360f78eaaba264c8bfe58ab0ba6791bd24))
* **internal:** remove extra empty newlines ([#51](https://github.com/straddleio/straddle-python/issues/51)) ([3877fae](https://github.com/straddleio/straddle-python/commit/3877fae25a2c9121c31f136df0dfffd45a352d45))
* **internal:** remove trailing character ([#73](https://github.com/straddleio/straddle-python/issues/73)) ([cc95339](https://github.com/straddleio/straddle-python/commit/cc9533903da76b684da7b2ead69b80430333f530))
* **internal:** remove unused http client options forwarding ([#46](https://github.com/straddleio/straddle-python/issues/46)) ([0589969](https://github.com/straddleio/straddle-python/commit/0589969a73aceae1468911681601083f89dc0414))
* **internal:** update client tests ([#38](https://github.com/straddleio/straddle-python/issues/38)) ([bcda27a](https://github.com/straddleio/straddle-python/commit/bcda27ac8e0bd67f174622d511e5d4b778f88008))
* **internal:** update conftest.py ([bb00a66](https://github.com/straddleio/straddle-python/commit/bb00a661f1160c8ef316567fcf9d098f82f1b406))
* **internal:** update models test ([7f7d7b2](https://github.com/straddleio/straddle-python/commit/7f7d7b25badc849d04a21cedb9e7738c273a7972))
* **internal:** update pyright settings ([bdee36f](https://github.com/straddleio/straddle-python/commit/bdee36fe1bd76d32d79cfa262aa80351c0305a53))
* **readme:** update badges ([457b5c6](https://github.com/straddleio/straddle-python/commit/457b5c61c6838b03521726869eb4033b2d235bd3))
* **tests:** add tests for httpx client instantiation & proxies ([cc9194e](https://github.com/straddleio/straddle-python/commit/cc9194ec63dbcf9ab1e99f78de7a25194dd04678))
* **tests:** run tests in parallel ([b12f260](https://github.com/straddleio/straddle-python/commit/b12f2609eeda766265f2e779ba84cb5857e12111))
* **tests:** skip some failing tests on the latest python versions ([02d4ca1](https://github.com/straddleio/straddle-python/commit/02d4ca15411d4546061938068a158b61a27383f2))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([8b30a61](https://github.com/straddleio/straddle-python/commit/8b30a6119e5874bf81d2dce70a69db68df2d07f9))
* remove private imports from datetime snippets ([0c11b44](https://github.com/straddleio/straddle-python/commit/0c11b44abf88a7eb8447e02fac3f40b270be4f05))
* revise readme docs about nested params ([#49](https://github.com/straddleio/straddle-python/issues/49)) ([9718178](https://github.com/straddleio/straddle-python/commit/971817812247bad919df996e4ceca571dae32631))
* swap examples used in readme ([#74](https://github.com/straddleio/straddle-python/issues/74)) ([ff0fa70](https://github.com/straddleio/straddle-python/commit/ff0fa70517962941c742a7fa68df5a5205fbbf07))
* update URLs from stainlessapi.com to stainless.com ([#44](https://github.com/straddleio/straddle-python/issues/44)) ([4f1feda](https://github.com/straddleio/straddle-python/commit/4f1fedae9c615e5640a2ccd6f8b6df6f9ccddd04))

## 0.1.0 (2025-01-29)

Full Changelog: [v0.1.0-alpha.5...v0.1.0](https://github.com/straddleio/straddle-python/compare/v0.1.0-alpha.5...v0.1.0)

### Features

* **api:** api update ([#10](https://github.com/straddleio/straddle-python/issues/10)) ([26ccbe0](https://github.com/straddleio/straddle-python/commit/26ccbe04110831d2faf214e5b2dd30a587dbe72a))
* **api:** api update ([#12](https://github.com/straddleio/straddle-python/issues/12)) ([1690d13](https://github.com/straddleio/straddle-python/commit/1690d13a7a90ec9cf14ae1a78c635c3e839a9fb9))
* **api:** Release Updates to SDK based on Open API Spec ([#11](https://github.com/straddleio/straddle-python/issues/11)) ([a6886a0](https://github.com/straddleio/straddle-python/commit/a6886a01575980ddbf29479c7b00fc409c16c97f))
* **api:** Release Updates to SDK based on Open API Spec ([#8](https://github.com/straddleio/straddle-python/issues/8)) ([731974f](https://github.com/straddleio/straddle-python/commit/731974f6db0ad41d26c65c351b7cd64a48ed3358))
* **api:** Remove current page number ([#5](https://github.com/straddleio/straddle-python/issues/5)) ([c01fabf](https://github.com/straddleio/straddle-python/commit/c01fabff73042ef75452eaeac776b6b6ddc5ac38))
* **api:** update via SDK Studio ([a7e901f](https://github.com/straddleio/straddle-python/commit/a7e901f61dac56f0bd79164509d8d64954ba1d68))
* **api:** update via SDK Studio ([41ebbd6](https://github.com/straddleio/straddle-python/commit/41ebbd6f32281254928008b3fb89d4b434374654))
* **api:** update via SDK Studio ([a75bd45](https://github.com/straddleio/straddle-python/commit/a75bd4560b1ea59c50629cbf1037dac7aff3981d))
* **api:** update via SDK Studio ([a94dda8](https://github.com/straddleio/straddle-python/commit/a94dda861a899f39a886a75c5b71bc14a9470f3c))
* **api:** update via SDK Studio ([3a9fe32](https://github.com/straddleio/straddle-python/commit/3a9fe32c43bf32cb4f502a74774db70055570324))
* **api:** update via SDK Studio ([6485927](https://github.com/straddleio/straddle-python/commit/6485927bf24a478c4072572ce5df6e05d0c94fea))
* **api:** update via SDK Studio ([5562edb](https://github.com/straddleio/straddle-python/commit/5562edbd9ed40b2126640ba341f76cbf140a541f))
* **api:** update via SDK Studio ([760224e](https://github.com/straddleio/straddle-python/commit/760224ed2bbdddb98cb8ea2fcafd2bd8139c8300))
* **api:** update via SDK Studio ([1d72df1](https://github.com/straddleio/straddle-python/commit/1d72df1eea232da8bbb53fb96b6094eb73b5d6a9))
* **api:** update via SDK Studio ([a3d251a](https://github.com/straddleio/straddle-python/commit/a3d251ae688ed92d4db3cee76698057bc6cf9f02))
* **api:** update via SDK Studio ([172a7fa](https://github.com/straddleio/straddle-python/commit/172a7fa998ef359c265504c2c2e592d49261d709))
* **api:** update via SDK Studio ([0800859](https://github.com/straddleio/straddle-python/commit/0800859bcf12016d1f88728045ed2c20d2664b99))
* **sdk:** Add unwrap response ([#17](https://github.com/straddleio/straddle-python/issues/17)) ([852aa05](https://github.com/straddleio/straddle-python/commit/852aa055711c355bd442d87c558d12e23b9e3918))
* **sdk:** Remove wrapper ([#18](https://github.com/straddleio/straddle-python/issues/18)) ([f2522b4](https://github.com/straddleio/straddle-python/commit/f2522b47b3bde8d3228288b2b15e063c635619d9))


### Bug Fixes

* **sdk:** Fix contact field ([#15](https://github.com/straddleio/straddle-python/issues/15)) ([872f428](https://github.com/straddleio/straddle-python/commit/872f428b2ff3b9d45d7eda14bcc39d307b2791d8))
* **sdk:** Fix Environment to point to correct URLs ([#13](https://github.com/straddleio/straddle-python/issues/13)) ([515a3b4](https://github.com/straddleio/straddle-python/commit/515a3b4e54029416e0db82d472905e9225739994))


### Chores

* go live ([#1](https://github.com/straddleio/straddle-python/issues/1)) ([d071421](https://github.com/straddleio/straddle-python/commit/d0714214b4b8cca97ed652f44b21ce6115fb4e2d))
* update SDK settings ([#3](https://github.com/straddleio/straddle-python/issues/3)) ([296cab7](https://github.com/straddleio/straddle-python/commit/296cab7bb45081c524f60eb01d3c78cd62a359c2))

## 0.1.0-alpha.5 (2025-01-29)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/straddleio/straddle-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** Release Updates to SDK based on Open API Spec ([#20](https://github.com/straddleio/straddle-python/issues/20)) ([b5a01fc](https://github.com/straddleio/straddle-python/commit/b5a01fc0a93c049fa3e4b723c712f45fb8c4a02c))
* **api:** Update Config to add versioning to DTOs. Add Shared models to avoid duplication where possible. ([#23](https://github.com/straddleio/straddle-python/issues/23)) ([85760de](https://github.com/straddleio/straddle-python/commit/85760de6a2cfc08b8d21370dce8804cdcf5f2cac))
* **docs:** Preliminary update to SDK Spec ([#24](https://github.com/straddleio/straddle-python/issues/24)) ([750a0a1](https://github.com/straddleio/straddle-python/commit/750a0a118b4e067ef1c7a607549f1d7935f1b486))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#22](https://github.com/straddleio/straddle-python/issues/22)) ([478dec0](https://github.com/straddleio/straddle-python/commit/478dec06567cf5e9ccbb41731d53381cb42b2de7))
* **docs:** Release Updates to SDK based on Open API Spec (Final) ([#25](https://github.com/straddleio/straddle-python/issues/25)) ([21af8e5](https://github.com/straddleio/straddle-python/commit/21af8e5aa7fcdef97a481a17a3efb15a5fe35394))

## 0.1.0-alpha.4 (2025-01-28)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/straddleio/straddle-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **sdk:** Add unwrap response ([#17](https://github.com/straddleio/straddle-python/issues/17)) ([dda7f97](https://github.com/straddleio/straddle-python/commit/dda7f9752cec074b048971a924fcaecdde991810))
* **sdk:** Remove wrapper ([#18](https://github.com/straddleio/straddle-python/issues/18)) ([9a5735c](https://github.com/straddleio/straddle-python/commit/9a5735c2bb91f28f8367b495e2afbce4ea1fcf67))


### Bug Fixes

* **sdk:** Fix contact field ([#15](https://github.com/straddleio/straddle-python/issues/15)) ([7d26929](https://github.com/straddleio/straddle-python/commit/7d26929db83a2bd7a5c00886bbbabd1a77ee5a69))

## 0.1.0-alpha.3 (2025-01-28)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/straddleio/straddle-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** api update ([#10](https://github.com/straddleio/straddle-python/issues/10)) ([26ccbe0](https://github.com/straddleio/straddle-python/commit/26ccbe04110831d2faf214e5b2dd30a587dbe72a))
* **api:** api update ([#12](https://github.com/straddleio/straddle-python/issues/12)) ([1690d13](https://github.com/straddleio/straddle-python/commit/1690d13a7a90ec9cf14ae1a78c635c3e839a9fb9))
* **api:** Release Updates to SDK based on Open API Spec ([#11](https://github.com/straddleio/straddle-python/issues/11)) ([a6886a0](https://github.com/straddleio/straddle-python/commit/a6886a01575980ddbf29479c7b00fc409c16c97f))
* **api:** Release Updates to SDK based on Open API Spec ([#8](https://github.com/straddleio/straddle-python/issues/8)) ([731974f](https://github.com/straddleio/straddle-python/commit/731974f6db0ad41d26c65c351b7cd64a48ed3358))


### Bug Fixes

* **sdk:** Fix Environment to point to correct URLs ([#13](https://github.com/straddleio/straddle-python/issues/13)) ([515a3b4](https://github.com/straddleio/straddle-python/commit/515a3b4e54029416e0db82d472905e9225739994))

## 0.1.0-alpha.2 (2025-01-27)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/straddleio/straddle-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** Remove current page number ([#5](https://github.com/straddleio/straddle-python/issues/5)) ([c01fabf](https://github.com/straddleio/straddle-python/commit/c01fabff73042ef75452eaeac776b6b6ddc5ac38))

## 0.1.0-alpha.1 (2025-01-27)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/straddleio/straddle-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([a7e901f](https://github.com/straddleio/straddle-python/commit/a7e901f61dac56f0bd79164509d8d64954ba1d68))
* **api:** update via SDK Studio ([41ebbd6](https://github.com/straddleio/straddle-python/commit/41ebbd6f32281254928008b3fb89d4b434374654))
* **api:** update via SDK Studio ([a75bd45](https://github.com/straddleio/straddle-python/commit/a75bd4560b1ea59c50629cbf1037dac7aff3981d))
* **api:** update via SDK Studio ([a94dda8](https://github.com/straddleio/straddle-python/commit/a94dda861a899f39a886a75c5b71bc14a9470f3c))
* **api:** update via SDK Studio ([3a9fe32](https://github.com/straddleio/straddle-python/commit/3a9fe32c43bf32cb4f502a74774db70055570324))
* **api:** update via SDK Studio ([6485927](https://github.com/straddleio/straddle-python/commit/6485927bf24a478c4072572ce5df6e05d0c94fea))
* **api:** update via SDK Studio ([5562edb](https://github.com/straddleio/straddle-python/commit/5562edbd9ed40b2126640ba341f76cbf140a541f))
* **api:** update via SDK Studio ([760224e](https://github.com/straddleio/straddle-python/commit/760224ed2bbdddb98cb8ea2fcafd2bd8139c8300))
* **api:** update via SDK Studio ([1d72df1](https://github.com/straddleio/straddle-python/commit/1d72df1eea232da8bbb53fb96b6094eb73b5d6a9))
* **api:** update via SDK Studio ([a3d251a](https://github.com/straddleio/straddle-python/commit/a3d251ae688ed92d4db3cee76698057bc6cf9f02))
* **api:** update via SDK Studio ([172a7fa](https://github.com/straddleio/straddle-python/commit/172a7fa998ef359c265504c2c2e592d49261d709))
* **api:** update via SDK Studio ([0800859](https://github.com/straddleio/straddle-python/commit/0800859bcf12016d1f88728045ed2c20d2664b99))


### Chores

* go live ([#1](https://github.com/straddleio/straddle-python/issues/1)) ([d071421](https://github.com/straddleio/straddle-python/commit/d0714214b4b8cca97ed652f44b21ce6115fb4e2d))
* update SDK settings ([#3](https://github.com/straddleio/straddle-python/issues/3)) ([296cab7](https://github.com/straddleio/straddle-python/commit/296cab7bb45081c524f60eb01d3c78cd62a359c2))
