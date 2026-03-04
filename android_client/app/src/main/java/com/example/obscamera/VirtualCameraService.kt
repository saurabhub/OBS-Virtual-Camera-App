package com.example.obscamera

import android.app.Service
import android.content.Intent
import android.graphics.BitmapFactory
import android.graphics.SurfaceTexture
import android.os.IBinder
import android.util.Log
import android.view.Surface
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.nio.ByteBuffer

class VirtualCameraService : Service() {

    private val TAG = "VirtualCameraService"
    private var isRunning = false
    private var udpSocket: DatagramSocket? = null
    private val PORT = 5005
    
    // This would be provided by your VirtualDisplay or Camera API implementation
    private var outputSurface: Surface? = null 

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!isRunning) {
            isRunning = true
            startUdpReceiver()
        }
        return START_STICKY
    }

    private fun startUdpReceiver() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                udpSocket = DatagramSocket(PORT)
                val receiveData = ByteArray(65535)
                
                Log.d(TAG, "UDP Receiver started on port $PORT")

                var frameBuffer = ByteArray(0)

                while (isRunning) {
                    val packet = DatagramPacket(receiveData, receiveData.size)
                    udpSocket?.receive(packet)
                    
                    // In a production app, you handle chunk reassembly here.
                    // Assuming we receive a complete JPEG or we append chunks:
                    val chunk = packet.data.copyOfRange(0, packet.length)
                    
                    // Decode JPEG to Bitmap
                    val bitmap = BitmapFactory.decodeByteArray(chunk, 0, chunk.size)
                    
                    bitmap?.let {
                        // Render bitmap to VirtualDisplay / SurfaceTexture Bridge
                        renderToSurface(it)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error in UDP Receiver: \${e.message}")
            }
        }
    }

    private fun renderToSurface(bitmap: android.graphics.Bitmap) {
        outputSurface?.let { surface ->
            val canvas = surface.lockCanvas(null)
            canvas?.let {
                it.drawBitmap(bitmap, 0f, 0f, null)
                surface.unlockCanvasAndPost(it)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        udpSocket?.close()
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
