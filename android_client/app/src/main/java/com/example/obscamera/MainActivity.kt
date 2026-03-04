package com.example.obscamera

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.Manifest
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.text.format.Formatter

class MainActivity : AppCompatActivity() {

    private val PERMISSION_REQUEST_CODE = 100
    private var isServiceRunning = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnStart = findViewById<Button>(R.id.btnStartService)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val tvIp = findViewById<TextView>(R.id.tvIpAddress)

        // Show Current IP
        tvIp.text = "Your IP Address:\n\${getLocalIpAddress()}"

        btnStart.setOnClickListener {
            if (checkAllPermissions()) {
                toggleService(btnStart, tvStatus)
            } else {
                requestPermissions()
            }
        }
        
        // Initial permission check on launch
        if (!checkAllPermissions()) {
            requestPermissions()
        }
    }

    private fun toggleService(btn: Button, status: TextView) {
        val intent = Intent(this, VirtualCameraService::class.java)
        if (!isServiceRunning) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
            isServiceRunning = true
            btn.text = "STOP VIRTUAL CAMERA"
            status.text = "Status: Running on Port 5005"
            status.setTextColor(ContextCompat.getColor(this, android.R.color.holo_green_dark))
        } else {
            stopService(intent)
            isServiceRunning = false
            btn.text = "START VIRTUAL CAMERA"
            status.text = "Status: Stopped"
            status.setTextColor(ContextCompat.getColor(this, android.R.color.darker_gray))
        }
    }

    private fun checkAllPermissions(): Boolean {
        // Check Camera Permission
        val cameraGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
        
        // Check Overlay Permission (System Alert Window)
        val alertWindowGranted = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Settings.canDrawOverlays(this)
        } else {
            true
        }

        return cameraGranted && alertWindowGranted
    }

    private fun requestPermissions() {
        val permissionsToRequest = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add(Manifest.permission.CAMERA)
        }

        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissionsToRequest.toTypedArray(), PERMISSION_REQUEST_CODE)
        }

        // Overlay permission requires a special intent in Android 6.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:\$packageName")
            )
            Toast.makeText(this, "Please allow 'Display over other apps'", Toast.LENGTH_LONG).show()
            startActivityForResult(intent, 200)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Camera Permission Granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Camera Permission Denied", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun getLocalIpAddress(): String {
        try {
            val wifiManager = applicationContext.getSystemService(WIFI_SERVICE) as WifiManager
            val wifiInfo = wifiManager.connectionInfo
            val ip = wifiInfo.ipAddress
            return Formatter.formatIpAddress(ip)
        } catch (ex: Exception) {
            return "Unable to get IP (Connect to Wi-Fi)"
        }
    }
}
