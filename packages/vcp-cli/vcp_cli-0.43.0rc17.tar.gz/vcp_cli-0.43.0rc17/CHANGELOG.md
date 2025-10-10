# Changelog

## [0.46.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.45.0...v0.46.0) (2025-10-02)


### Features

* phase1 - foundational changes for refactoring model commands. ([#176](https://github.com/chanzuckerberg/vcp-cli/issues/176)) ([fdb89bc](https://github.com/chanzuckerberg/vcp-cli/commit/fdb89bce3d423b466ab7c3adf97c1adb55ba2539))


### Bug Fixes

* download command fails ([#190](https://github.com/chanzuckerberg/vcp-cli/issues/190)) ([e56a3be](https://github.com/chanzuckerberg/vcp-cli/commit/e56a3be621e428808013ba8bae5bea838298d710))

## [0.45.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.44.0...v0.45.0) (2025-10-01)


### Features

* Data CLI documentation ([#171](https://github.com/chanzuckerberg/vcp-cli/issues/171)) ([00e5d7e](https://github.com/chanzuckerberg/vcp-cli/commit/00e5d7ecd98df1f96dcfafb61809a33623db0a85))


### Bug Fixes

* constrain cz-benchmarks version; caching bug fixes ([#178](https://github.com/chanzuckerberg/vcp-cli/issues/178)) ([bbfbec9](https://github.com/chanzuckerberg/vcp-cli/commit/bbfbec9ca6b583b1b2b7e34971c57132dcb34152))
* random seed not defaulting ([#173](https://github.com/chanzuckerberg/vcp-cli/issues/173)) ([adc0233](https://github.com/chanzuckerberg/vcp-cli/commit/adc0233aa824fe71eccefc8474265fe30c2e77bb))


### Documentation

* Fix CLI command name in docs ([#183](https://github.com/chanzuckerberg/vcp-cli/issues/183)) ([89ea6c2](https://github.com/chanzuckerberg/vcp-cli/commit/89ea6c2e2507436a481ee40a23d451e8de7c283c))
* updates ([#187](https://github.com/chanzuckerberg/vcp-cli/issues/187)) ([b59518b](https://github.com/chanzuckerberg/vcp-cli/commit/b59518b903dbd3daaf6be72acab26aa39c3b7d59))

## [0.44.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.43.0...v0.44.0) (2025-09-30)


### Features

* data search --help upgrades ([#166](https://github.com/chanzuckerberg/vcp-cli/issues/166)) ([d8cceb8](https://github.com/chanzuckerberg/vcp-cli/commit/d8cceb832fac319e845849922fbb37bbca0b9297))
* Error handling ([#154](https://github.com/chanzuckerberg/vcp-cli/issues/154)) ([b09b433](https://github.com/chanzuckerberg/vcp-cli/commit/b09b4339fad778dee6c96ad32e275b7c560639f6))
* fix scout; data --help ([#126](https://github.com/chanzuckerberg/vcp-cli/issues/126)) ([b5ce187](https://github.com/chanzuckerberg/vcp-cli/commit/b5ce187834ca655a5f8c7db14627a9c3909565aa))
* include `domain` in data search and describe commands ([#158](https://github.com/chanzuckerberg/vcp-cli/issues/158)) ([5d515b1](https://github.com/chanzuckerberg/vcp-cli/commit/5d515b117cd103d610ef668a93b2ef1546b35277))
* rename workflow command to assist ([#141](https://github.com/chanzuckerberg/vcp-cli/issues/141)) ([fc8b557](https://github.com/chanzuckerberg/vcp-cli/commit/fc8b557149f61cc8f1853f911d3afdc488b5ae41))
* search and download parity ([#155](https://github.com/chanzuckerberg/vcp-cli/issues/155)) ([efcc940](https://github.com/chanzuckerberg/vcp-cli/commit/efcc9400e5fb147649141d7e267fe5b3c7e7a32d))
* show file size in search --full, describe, and download commands (data) ([#153](https://github.com/chanzuckerberg/vcp-cli/issues/153)) ([1eacce0](https://github.com/chanzuckerberg/vcp-cli/commit/1eacce040b4cb54f33f7d5355a3ad2045fb18a9b))
* update feature flag system to automatically hide the vcp data credentials cmd ([#148](https://github.com/chanzuckerberg/vcp-cli/issues/148)) ([42522da](https://github.com/chanzuckerberg/vcp-cli/commit/42522dad6ddb40cb959906390dc899415c5d0689))
* Validate model metadata against ModelHub ([#123](https://github.com/chanzuckerberg/vcp-cli/issues/123)) ([65a899a](https://github.com/chanzuckerberg/vcp-cli/commit/65a899a3e0ca4cc522353f48a28120fdb02b72f4))
* VC-4086 Improve cli startup time ([#136](https://github.com/chanzuckerberg/vcp-cli/issues/136)) ([91c615f](https://github.com/chanzuckerberg/vcp-cli/commit/91c615ff951b3472a3c3119b3b0edae7c296d34c))


### Bug Fixes

* allow downloads on public s3 buckets ([#170](https://github.com/chanzuckerberg/vcp-cli/issues/170)) ([6ac5e58](https://github.com/chanzuckerberg/vcp-cli/commit/6ac5e5879fcccf2f6c4ad546a0ed331ffa383f78))
* better message for 5xx errors ([#162](https://github.com/chanzuckerberg/vcp-cli/issues/162)) ([18670ad](https://github.com/chanzuckerberg/vcp-cli/commit/18670ad9d9b563051ef9a81326ecbd0b6399f2ca))
* cli version ([#133](https://github.com/chanzuckerberg/vcp-cli/issues/133)) ([9816b35](https://github.com/chanzuckerberg/vcp-cli/commit/9816b35fdc072df4d74b59354f6ff25adb592485))
* dataclasses don't magically handle Pydantic fields ([#127](https://github.com/chanzuckerberg/vcp-cli/issues/127)) ([06d4d59](https://github.com/chanzuckerberg/vcp-cli/commit/06d4d59c8945bfb3118decf8268bac6314bf5226))
* dataset id format fix ([#165](https://github.com/chanzuckerberg/vcp-cli/issues/165)) ([1a89ddb](https://github.com/chanzuckerberg/vcp-cli/commit/1a89ddb23e5164e604cd7274b50d50056a5a45c1))
* download regression ([#161](https://github.com/chanzuckerberg/vcp-cli/issues/161)) ([f1058da](https://github.com/chanzuckerberg/vcp-cli/commit/f1058da946c5fb627d69fcab31075cd019d0279a))
* fix types for scopes & citation ([#146](https://github.com/chanzuckerberg/vcp-cli/issues/146)) ([7094806](https://github.com/chanzuckerberg/vcp-cli/commit/7094806f85d57cb950c91aa478a8f4e7fc3d71d9))
* fixes issue where vcp data search fails to show results when license is empty ([#128](https://github.com/chanzuckerberg/vcp-cli/issues/128)) ([c4fa184](https://github.com/chanzuckerberg/vcp-cli/commit/c4fa1842c7d798a6b3dca1a2b13eb8b7761769d7))
* fixes vcp data describe ([#130](https://github.com/chanzuckerberg/vcp-cli/issues/130)) ([0872254](https://github.com/chanzuckerberg/vcp-cli/commit/08722545d3e67a0fe560c4516d8073d60cdf6e36))
* include config.yaml in distro ([#131](https://github.com/chanzuckerberg/vcp-cli/issues/131)) ([28fb1ae](https://github.com/chanzuckerberg/vcp-cli/commit/28fb1aeb02f1958b97a2f54cccafa1887e3b98be))
* minor config fixes for data command ([#147](https://github.com/chanzuckerberg/vcp-cli/issues/147)) ([255f2cc](https://github.com/chanzuckerberg/vcp-cli/commit/255f2ccc7b4f28f76bd1afdb90d342ecdfb7454d))
* Multiple datasets, multiple cell representation and multiple user dataset support ([#150](https://github.com/chanzuckerberg/vcp-cli/issues/150)) ([eca7fd0](https://github.com/chanzuckerberg/vcp-cli/commit/eca7fd06fe4821a4caba26817e08c25f67e3425b))
* temp fix for keywords (should be a List[str]) ([#143](https://github.com/chanzuckerberg/vcp-cli/issues/143)) ([6520ae7](https://github.com/chanzuckerberg/vcp-cli/commit/6520ae7d8825c30bbdcc3a2da9f5291eeb721f21))


### Documentation

* Add sphinx-click automated cli docs ([#132](https://github.com/chanzuckerberg/vcp-cli/issues/132)) ([83ab2df](https://github.com/chanzuckerberg/vcp-cli/commit/83ab2dfeeb08a8bed4c87c8991f68765de9729dd))
* fix doc build ([#149](https://github.com/chanzuckerberg/vcp-cli/issues/149)) ([4ee9c57](https://github.com/chanzuckerberg/vcp-cli/commit/4ee9c575c9c9812730436231a012be3c8ddc06b0))
* fixes in search --help ([#139](https://github.com/chanzuckerberg/vcp-cli/issues/139)) ([e155e62](https://github.com/chanzuckerberg/vcp-cli/commit/e155e62d1f5906c6d383c737212b3b297d3a8d82))
* VC-4458 update benchmark usage ([#157](https://github.com/chanzuckerberg/vcp-cli/issues/157)) ([d69426c](https://github.com/chanzuckerberg/vcp-cli/commit/d69426c25f65f3fc48722c91c77a4b2d429ae7b4))

## [0.43.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.42.0...v0.43.0) (2025-09-18)


### Features

* add `data summary` command, facet datasets by field ([#115](https://github.com/chanzuckerberg/vcp-cli/issues/115)) ([5bb45a4](https://github.com/chanzuckerberg/vcp-cli/commit/5bb45a45a71ca008859a09dd614ed73ceeee26dd))
* add license and doi to vcp data search --full ([#114](https://github.com/chanzuckerberg/vcp-cli/issues/114)) ([0a54c29](https://github.com/chanzuckerberg/vcp-cli/commit/0a54c29cd4afaa9a1ea29bef9dea7f55f96e948a))
* add user-agent header and centralized HTTP utilities ([#93](https://github.com/chanzuckerberg/vcp-cli/issues/93)) ([6649919](https://github.com/chanzuckerberg/vcp-cli/commit/664991981a5bec8574850845443cb274d601ad29))
* Centralize GitHub authentication across all model commands ([#110](https://github.com/chanzuckerberg/vcp-cli/issues/110)) ([0d1cade](https://github.com/chanzuckerberg/vcp-cli/commit/0d1cadef247aaac8edf46ebf26d0a2a7c2edccbc))
* Enabling exact match for search ([#112](https://github.com/chanzuckerberg/vcp-cli/issues/112)) ([ba2b091](https://github.com/chanzuckerberg/vcp-cli/commit/ba2b0918e192dd5e611b743a728e472b796cdbde))
* extend `data search --help` with searchable field explanations ([#121](https://github.com/chanzuckerberg/vcp-cli/issues/121)) ([5c89091](https://github.com/chanzuckerberg/vcp-cli/commit/5c89091bb224e1986c0ed81ac6436cbbe94dec9b))
* Feature flags to disable model and data commands ([#111](https://github.com/chanzuckerberg/vcp-cli/issues/111)) ([22f6ce8](https://github.com/chanzuckerberg/vcp-cli/commit/22f6ce841a7b571bd62527615eee57ffdb5ec8f0))
* Fix workflow validation for mlflow_pkg naming conventions ([#124](https://github.com/chanzuckerberg/vcp-cli/issues/124)) ([d7b69a7](https://github.com/chanzuckerberg/vcp-cli/commit/d7b69a7d93698caf1dc082151777ba2229543c97))
* improve error handling for vcp data describe &lt;invalid-id&gt; ([#116](https://github.com/chanzuckerberg/vcp-cli/issues/116)) ([5ac776b](https://github.com/chanzuckerberg/vcp-cli/commit/5ac776baf7fb488a4a9b6df91d81efb88334f889))
* improved downloads ([#81](https://github.com/chanzuckerberg/vcp-cli/issues/81)) ([48912c3](https://github.com/chanzuckerberg/vcp-cli/commit/48912c3df5d5cdf165ed870a836d57a44ee19e70))
* passing user dataset to model adapter ([#95](https://github.com/chanzuckerberg/vcp-cli/issues/95)) ([786037e](https://github.com/chanzuckerberg/vcp-cli/commit/786037e266b89aa4956e918f7f27168ac2878d09))
* review comments fixed ([#97](https://github.com/chanzuckerberg/vcp-cli/issues/97)) ([944f794](https://github.com/chanzuckerberg/vcp-cli/commit/944f794caf3acc0d2de4bd663ac4f07a4e518be1))
* vcp data describe should include XMS in tabular format ([#101](https://github.com/chanzuckerberg/vcp-cli/issues/101)) ([f50c957](https://github.com/chanzuckerberg/vcp-cli/commit/f50c9572f3f209814bbef4e0664620bda4ea96bf))


### Bug Fixes

* benchmark run user dataset option ([#109](https://github.com/chanzuckerberg/vcp-cli/issues/109)) ([34ef1bf](https://github.com/chanzuckerberg/vcp-cli/commit/34ef1bfbaaa157fea515797673072754cd9efc95))
* benchmarks version, change model dir ([#117](https://github.com/chanzuckerberg/vcp-cli/issues/117)) ([e75ffae](https://github.com/chanzuckerberg/vcp-cli/commit/e75ffaed0aa6d53e233802a607122238bca83d4e))
* get the publish to pypi action working ([#119](https://github.com/chanzuckerberg/vcp-cli/issues/119)) ([0162a05](https://github.com/chanzuckerberg/vcp-cli/commit/0162a05bc39a16ba0d01406eefc46bcb430a0c6b))
* resolve authentication issue and add verbose logging to model init ([#96](https://github.com/chanzuckerberg/vcp-cli/issues/96)) ([ced6724](https://github.com/chanzuckerberg/vcp-cli/commit/ced6724e77340849358d29fb2fe420d0c59ba431))
* resubmission workflow validation for stage command ([#106](https://github.com/chanzuckerberg/vcp-cli/issues/106)) ([a2d897b](https://github.com/chanzuckerberg/vcp-cli/commit/a2d897bdc3609301e10a1db0c182836776665df0))
* unbound TokenManager ([#100](https://github.com/chanzuckerberg/vcp-cli/issues/100)) ([4c2ae41](https://github.com/chanzuckerberg/vcp-cli/commit/4c2ae41fafa58ab340b354fbfaa00a2cfe50dec6))
* Warn user for unsupported dataset and task ([#102](https://github.com/chanzuckerberg/vcp-cli/issues/102)) ([b5c0cde](https://github.com/chanzuckerberg/vcp-cli/commit/b5c0cde606704a989253949b8f46e2d896c929ec))


### Documentation

* add basic documentation for VCP CLI (VCP-3228) ([#105](https://github.com/chanzuckerberg/vcp-cli/issues/105)) ([cf2374a](https://github.com/chanzuckerberg/vcp-cli/commit/cf2374af536736b4f014fe40522c2a828e7366b5))

## [0.42.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.41.0...v0.42.0) (2025-09-09)


### Features

* add model status command and workflow functionality ([#92](https://github.com/chanzuckerberg/vcp-cli/issues/92)) ([a2da84f](https://github.com/chanzuckerberg/vcp-cli/commit/a2da84fe5da96d7ac5011bacc04627f804c65fb5))
* implement refresh_token flow ([#88](https://github.com/chanzuckerberg/vcp-cli/issues/88)) ([fcf2b98](https://github.com/chanzuckerberg/vcp-cli/commit/fcf2b98444dcfb568cadbdc02c2a3a759942a5d2))
* improve data search table UI with Rich tables and dynamic pagination ([#83](https://github.com/chanzuckerberg/vcp-cli/issues/83)) ([1159df6](https://github.com/chanzuckerberg/vcp-cli/commit/1159df67316958467ad0fdb5cb25469987e5e84e))
* improve model init command ([#90](https://github.com/chanzuckerberg/vcp-cli/issues/90)) ([7534ec0](https://github.com/chanzuckerberg/vcp-cli/commit/7534ec0601d007f1c287ef71c033533561a976df))
* search - show total matches and paginated progress ([#87](https://github.com/chanzuckerberg/vcp-cli/issues/87)) ([a4af991](https://github.com/chanzuckerberg/vcp-cli/commit/a4af991037e099d3614dc97afb1b5350d08d7f49))
* VC-4055 uptake benchmark api in vcp cli ([#84](https://github.com/chanzuckerberg/vcp-cli/issues/84)) ([f69a01b](https://github.com/chanzuckerberg/vcp-cli/commit/f69a01ba1a73ba39e93e2daf27bf6406f2fdb617))

## [0.41.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.40.0...v0.41.0) (2025-09-04)


### Features

* add conditional scopes column to dataset search results ([#53](https://github.com/chanzuckerberg/vcp-cli/issues/53)) ([4eb95f0](https://github.com/chanzuckerberg/vcp-cli/commit/4eb95f0ea28b1a6bc2718143fcf07e5dd27554b1))
* Add initial docs pages ([#68](https://github.com/chanzuckerberg/vcp-cli/issues/68)) ([abd8cfe](https://github.com/chanzuckerberg/vcp-cli/commit/abd8cfe766bb150cb853e6369ce3181c57423f7c))
* add model stage command with batch upload functionality ([#75](https://github.com/chanzuckerberg/vcp-cli/issues/75)) ([e3db8fe](https://github.com/chanzuckerberg/vcp-cli/commit/e3db8fea73ea47b7e08bc8c5b1668eaaa42c07a6))
* Add Neuroglancer data preview command ([#80](https://github.com/chanzuckerberg/vcp-cli/issues/80)) ([a58d285](https://github.com/chanzuckerberg/vcp-cli/commit/a58d285a6729623dd3f4ef48866fc83255393b2f))
* **auth:** refactor logout to use Cognito token invalidation ([#61](https://github.com/chanzuckerberg/vcp-cli/issues/61)) ([8899e60](https://github.com/chanzuckerberg/vcp-cli/commit/8899e6040f680a314fbdc1a18a675f34ead888b2))
* benchmark list, run, get commands ([#71](https://github.com/chanzuckerberg/vcp-cli/issues/71)) ([bbba9f5](https://github.com/chanzuckerberg/vcp-cli/commit/bbba9f5cb805a196d501fe0530625bc0b81a048e))
* refactor model download to use presigned S3 URLs ([#69](https://github.com/chanzuckerberg/vcp-cli/issues/69)) ([f3c6c48](https://github.com/chanzuckerberg/vcp-cli/commit/f3c6c488fb31ac9e1e4471c82d5ea6720886150b))


### Bug Fixes

* get build and tests working again ([#76](https://github.com/chanzuckerberg/vcp-cli/issues/76)) ([4d2033c](https://github.com/chanzuckerberg/vcp-cli/commit/4d2033c7e8bdcfe974e1b603a47a287310ea4835))
* make workflow manually runnable ([#67](https://github.com/chanzuckerberg/vcp-cli/issues/67)) ([1ae6098](https://github.com/chanzuckerberg/vcp-cli/commit/1ae60986a09b568e0d3883cb5a3d1b54208f8238))
* resolve model staging authentication and update configuration structure ([#82](https://github.com/chanzuckerberg/vcp-cli/issues/82)) ([944d2a3](https://github.com/chanzuckerberg/vcp-cli/commit/944d2a3c07e7574c96859d333c5599ffeb5f7bdb))


### Documentation

* add github action for publishing docs to pages (VC-3228) ([#66](https://github.com/chanzuckerberg/vcp-cli/issues/66)) ([84c95f3](https://github.com/chanzuckerberg/vcp-cli/commit/84c95f3a8e68a0ce1d7ff605abfa2320f73de91c))
* fix repo urls in readme ([#63](https://github.com/chanzuckerberg/vcp-cli/issues/63)) ([03b55d9](https://github.com/chanzuckerberg/vcp-cli/commit/03b55d9f3a92448154198a909fe5952d07afe51e))

## [0.40.0](https://github.com/chanzuckerberg/vcp-cli/compare/v0.39.0...v0.40.0) (2025-08-25)


### Features

* testing release-please ([7e63e56](https://github.com/chanzuckerberg/vcp-cli/commit/7e63e56d6c73c74f595a6de2893be2c3bb3507a6))
