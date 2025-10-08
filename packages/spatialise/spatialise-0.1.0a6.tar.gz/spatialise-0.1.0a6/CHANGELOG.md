# Changelog

## 0.1.0-alpha.6 (2025-09-20)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/spatiali-se/spatialise-python/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* improve future compat with pydantic v3 ([cd589e3](https://github.com/spatiali-se/spatialise-python/commit/cd589e328eca7311fa5fe47d45cc18271ad82a2b))
* **types:** replace List[str] with SequenceNotStr in params ([c2a07ed](https://github.com/spatiali-se/spatialise-python/commit/c2a07edede235745702dd94de1b43b68ef392077))


### Bug Fixes

* avoid newer type syntax ([66389db](https://github.com/spatiali-se/spatialise-python/commit/66389db4a7580fc1c5e37ab9498e7a7a382f53bf))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([5860421](https://github.com/spatiali-se/spatialise-python/commit/5860421f18df4b72d0d6dd72bea5bc4d6039fed5))
* **internal:** add Sequence related utils ([bc84646](https://github.com/spatiali-se/spatialise-python/commit/bc846464eb596824ddfe74022e85a4fe2696513f))
* **internal:** change ci workflow machines ([1687bfe](https://github.com/spatiali-se/spatialise-python/commit/1687bfe8f06437c40e03a16762043ddc32098d55))
* **internal:** codegen related update ([ba0bb84](https://github.com/spatiali-se/spatialise-python/commit/ba0bb84d8d72fa8b45facc280d4fc65026a61179))
* **internal:** move mypy configurations to `pyproject.toml` file ([9d39b2a](https://github.com/spatiali-se/spatialise-python/commit/9d39b2a6900541cd7a8633492c46b6549893a476))
* **internal:** update comment in script ([08fbf7b](https://github.com/spatiali-se/spatialise-python/commit/08fbf7bfccea7c19544e4db45503524140d0d0a2))
* **internal:** update pydantic dependency ([8030cf6](https://github.com/spatiali-se/spatialise-python/commit/8030cf68d1c1ca753b4bf7248350d9f151380edf))
* **internal:** update pyright exclude list ([51e357c](https://github.com/spatiali-se/spatialise-python/commit/51e357c034e7bcda85a86c0ac3b1c80901c77ddc))
* **tests:** simplify `get_platform` test ([12e48c4](https://github.com/spatiali-se/spatialise-python/commit/12e48c430b434bf51d350a8de95a3ea5d1b85ae6))
* **types:** change optional parameter type from NotGiven to Omit ([69ed78f](https://github.com/spatiali-se/spatialise-python/commit/69ed78fcf72c1bda150446e8f9f00cf5a3a5ab8a))
* update github action ([da60df4](https://github.com/spatiali-se/spatialise-python/commit/da60df4c409d277162572de7b836a0b1cd80679b))

## 0.1.0-alpha.5 (2025-08-09)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/spatiali-se/spatialise-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Chores

* **internal:** fix ruff target version ([dd94147](https://github.com/spatiali-se/spatialise-python/commit/dd941471edafa39aa6c27819a66862105780e94b))
* update @stainless-api/prism-cli to v5.15.0 ([a265f34](https://github.com/spatiali-se/spatialise-python/commit/a265f34eed057447601160003c73e72316d0f1df))

## 0.1.0-alpha.4 (2025-08-04)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/spatiali-se/spatialise-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **api:** update via SDK Studio ([8119a36](https://github.com/spatiali-se/spatialise-python/commit/8119a362880fea3c85af1d67b643e691846b2e04))

## 0.1.0-alpha.3 (2025-08-02)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/spatiali-se/spatialise-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** update via SDK Studio ([69a7e93](https://github.com/spatiali-se/spatialise-python/commit/69a7e9355f0e955b4416095c3f514feb9d8014a4))

## 0.1.0-alpha.2 (2025-08-02)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/spatiali-se/spatialise-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** update via SDK Studio ([e98a272](https://github.com/spatiali-se/spatialise-python/commit/e98a272604c153b3408c7e5f405646792690670b))
* **api:** update via SDK Studio ([1aa4efe](https://github.com/spatiali-se/spatialise-python/commit/1aa4efe966df52cf88da7a7a50c5091d07b07e7e))
* **api:** update via SDK Studio ([551a5f0](https://github.com/spatiali-se/spatialise-python/commit/551a5f0d8e8fa272de4411d0af771b1eab6bd12c))
* **api:** update via SDK Studio ([39777b0](https://github.com/spatiali-se/spatialise-python/commit/39777b032f176e2ea67304a14daa853c032344bb))

## 0.1.0-alpha.1 (2025-08-01)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/spatiali-se/spatialise-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([1b8187f](https://github.com/spatiali-se/spatialise-python/commit/1b8187fd7398ee9e3019fc3dc4c1e78951b089b8))
* **client:** support file upload requests ([49c90b0](https://github.com/spatiali-se/spatialise-python/commit/49c90b05fbb2e5ad9b613a51c0ab14971edc66b7))


### Bug Fixes

* enable GitHub Actions workflows for all pull requests ([3d6ecca](https://github.com/spatiali-se/spatialise-python/commit/3d6eccacfa5e0be7e7e85a0e95e9835c1bf8e62e))


### Chores

* sync repo ([9696d8b](https://github.com/spatiali-se/spatialise-python/commit/9696d8ba32bef8199bc2c56a00183ae5851ff3c9))
* update SDK settings ([3e73e00](https://github.com/spatiali-se/spatialise-python/commit/3e73e00b3cae0cfc789d5f2596c9915092dcd418))
* update SDK settings ([a76165b](https://github.com/spatiali-se/spatialise-python/commit/a76165b7f411c3c9eb3205910fd2d1d13ccbc38b))
