from sifts.core.types import Language

TEST_GLOBS = {
    Language.Python: [
        "test*",  # Python
        "*test.py",  # Python
    ],
    Language.JavaScript: [
        "*.spec.js",  # JavaScript
        "*.test.js",  # JavaScript
    ],
    Language.TypeScript: [
        "*.spec.ts",  # TypeScript
        "*.test.ts",  # TypeScript
    ],
    Language.Java: [
        "*Test.java",  # Java
    ],
    Language.Kotlin: [
        "*Test.kt",  # Kotlin
    ],
    Language.Go: [
        "*_test.go",  # Go
    ],
    Language.Ruby: [
        "*_test.rb",  # Ruby
    ],
    Language.CSharp: [
        "*.Tests.cs",  # C#
    ],
    Language.Swift: [
        "*Test.swift",  # Swift
    ],
}

CONFIG_FILES = {
    Language.Java: [
        "pom.xml",
        "build.gradle",
        "settings.gradle",
        "MANIFEST.MF",
        "application.properties",
        "application.yml",
        "log4j.properties",
        "web.xml",
        "hibernate.cfg.xml",
        "persistence.xml",
    ],
    Language.Python: [
        "requirements.txt",
        "setup.py",
        "Pipfile",
        "pyproject.toml",
        "tox.ini",
        "pytest.ini",
        "mypy.ini",
        ".pylintrc",
        ".flake8",
        "config.yaml",
    ],
    Language.JavaScript: [
        "package.json",
        "package-lock.json",
        ".babelrc",
        "webpack.config.js",
        ".eslintrc.js",
        ".prettierrc",
        "tsconfig.json",
        "jest.config.js",
        ".env",
        "gruntfile.js",
    ],
    Language.PHP: [
        "composer.json",
        "composer.lock",
        "php.ini",
        "phpunit.xml",
        "config.php",
        "symfony.lock",
        "artisan",
        ".env",
    ],
    Language.CSharp: [
        "app.config",
        "web.config",
        "packages.config",
        "nuget.config",
        "Directory.Build.props",
        "Directory.Build.targets",
        "global.json",
    ],
    Language.Go: [
        "go.mod",
        "go.sum",
        ".golangci.yml",
        "Gopkg.toml",
        "Gopkg.lock",
        "glide.yaml",
        "glide.lock",
    ],
    Language.Ruby: [
        "Gemfile",
        "Gemfile.lock",
        ".ruby-version",
        ".rubocop.yml",
        "Rakefile",
        "config.ru",
        "database.yml",
        "boot.rb",
    ],
    Language.JavaScript: [
        "tsconfig.json",
        "package.json",
        "package-lock.json",
        ".eslintrc.js",
        ".prettierrc",
        "webpack.config.js",
        "jest.config.js",
        ".env",
    ],
    Language.Kotlin: [
        "build.gradle.kts",
        "settings.gradle.kts",
        "pom.xml",
        "gradle.properties",
        "gradlew",
        "gradlew.bat",
        "settings.gradle",
        "build.gradle",
    ],
    Language.Swift: [
        "Package.swift",
        "Config.xcconfig",
        "Info.plist",
        "project.pbxproj",
        ".swiftlint.yml",
        "Cartfile",
        "Cartfile.resolved",
        "Podfile",
        "Podfile.lock",
    ],
}


EXCLUDE_DIRS = [
    "assets",
    "target",
    "build",
    ".gradle",
    ".mvn",
    ".idea",
    "out",
    "src/test",
    "tests",
    "__tests__",
    "spec",
    ".venv",
    "__pycache__",
    "dist",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".cache",
    "vendor",
    ".composer",
    "bin",
    "obj",
    ".vs",
    "packages",
    ".vscode",
    "pkg",
    ".bundle",
    "tmp",
    ".build",
    "Carthage",
    "Pods",
    "DerivedData",
    "cache",
    ".ruff_cache",
    ".metals",
    ".bloop",
    "wwwroot",
    "plugin",
    "plugins",
    "libraries",
    "target/deps",
    ".stack-work",
    "dist-newstyle",
    ".dart_tool",
    "deps",
    "_build",
    "checkouts",
    "target/scala-*",
    # archivos/artifacts
    "*.min.js",
    "*.min.css",
    "*.jar",
    "*.war",
    "*.ear",
    "*.jmod",
    "*.nupkg",
    "*.gem",
    "*.phar*",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.a",
    "*.lib",
    "*.rlib",
    "*.rs.bk",
    "*.rs",
    "Cargo.lock",
    "Cargo.toml",
    "gradlew*",
    "*mock*",
]


TEST_FILES = [x for item in TEST_GLOBS.values() for x in item]
