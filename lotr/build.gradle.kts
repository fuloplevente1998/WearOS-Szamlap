plugins { id("com.android.application") }

android {
    enableKotlin = false
    namespace = "hu.fuloplevente.onering"
    compileSdk = 36
    defaultConfig {
        applicationId = "hu.fuloplevente.onering"
        minSdk = 34
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-test"
    }
    buildTypes {
        debug {
            // R8 removes the generated R classes so the WFF APK contains no DEX.
            isMinifyEnabled = true
            // Keep readable resource paths in the test APK for inspection.
            isDebuggable = true
            isShrinkResources = false
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = false
        }
    }
    lint {
        // Android lint does not follow the resource names inside WFF raw XML.
        disable += "UnusedResources"
    }
}
