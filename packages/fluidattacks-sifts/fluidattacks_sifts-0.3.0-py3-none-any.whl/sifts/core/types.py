from enum import Enum


class Language(Enum):
    Swift = "swift"
    CSharp = "csharp"
    Go = "golang"
    FuzzyTestLang = "fuzzy_test_lang"
    Java = "Java"
    Python = "Python"
    PHP = "PHP"
    Ruby = "Ruby"
    C = "C"
    Kotlin = "Kotlin"
    Ghidra = "Ghidra"
    JavaScript = "JavaScript"
    TypeScript = "TypeScript"
    LLVM = "LLVM"
    NewC = "newc"
    Scala = "Scala"

    def __str__(self) -> str:
        return self.value
