plugins { id("com.android.application") }

android {
    enableKotlin = false
    namespace = "hu.fuloplevente.spartannight"
    compileSdk = 36
    defaultConfig {
        applicationId = "hu.fuloplevente.spartannight"
        minSdk = 34
        targetSdk = 36
        versionCode = 6
        versionName = "0.1.5-test"
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
            // Production signing is deliberately supplied separately from test signing.
        }
    }
    lint {
        // Android lint does not follow the resource names inside WFF raw XML.
        // scripts/check-package.py checks every such reference against the APK.
        disable += "UnusedResources"
    }
}
