plugins { id("com.android.application") }

android {
    enableKotlin = false
    namespace = "hu.fuloplevente.oneringwatchface"
    compileSdk = 36
    defaultConfig {
        applicationId = "hu.fuloplevente.oneringwatchface"
        minSdk = 34
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-test"
    }
    buildTypes {
        debug {
            isMinifyEnabled = true
            isDebuggable = true
            isShrinkResources = false
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = false
        }
    }
    lint { disable += "UnusedResources" }
}
