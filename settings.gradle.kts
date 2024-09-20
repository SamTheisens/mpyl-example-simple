rootProject.name = "gradle-multi-module"
include("projects:gradle1", "projects:gradle2")

dependencyResolutionManagement {
    versionCatalogs {
        create("libs") {
            from(files("libs.versions.toml"))
        }

    }
}