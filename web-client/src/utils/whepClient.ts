/**
 * WHEP (WebRTC-HTTP Egress Protocol) 客户端
 * 用于从MediaMTX服务器播放WebRTC流
 */

export class WHEPClient {
  private pc: RTCPeerConnection | null = null
  private videoElement: HTMLVideoElement
  private whepUrl: string
  private restartTimeout: number | null = null

  constructor(videoElement: HTMLVideoElement, whepUrl: string) {
    this.videoElement = videoElement
    this.whepUrl = whepUrl
  }

  async start(): Promise<void> {
    console.log('Starting WHEP client for:', this.whepUrl)

    // 创建 RTCPeerConnection
    this.pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
      bundlePolicy: 'max-bundle'
    })

    // 监听 track 事件
    this.pc.ontrack = (event) => {
      console.log('Received track:', event.track.kind)
      if (this.videoElement.srcObject !== event.streams[0]) {
        this.videoElement.srcObject = event.streams[0]
        console.log('Set video srcObject')
      }
    }

    // 监听连接状态
    this.pc.onconnectionstatechange = () => {
      console.log('Connection state:', this.pc?.connectionState)
      if (this.pc?.connectionState === 'failed' || this.pc?.connectionState === 'disconnected') {
        this.scheduleRestart()
      }
    }

    // 添加 transceiver 用于接收视频
    this.pc.addTransceiver('video', { direction: 'recvonly' })
    this.pc.addTransceiver('audio', { direction: 'recvonly' })

    // 创建 offer
    const offer = await this.pc.createOffer()
    await this.pc.setLocalDescription(offer)

    // 发送 offer 到 WHEP 端点
    const response = await fetch(this.whepUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/sdp'
      },
      body: offer.sdp
    })

    if (!response.ok) {
      throw new Error(`WHEP request failed: ${response.status} ${response.statusText}`)
    }

    // 获取 answer
    const answerSdp = await response.text()
    await this.pc.setRemoteDescription({
      type: 'answer',
      sdp: answerSdp
    })

    console.log('WHEP client started successfully')
  }

  private scheduleRestart(): void {
    if (this.restartTimeout !== null) {
      return
    }

    this.restartTimeout = window.setTimeout(() => {
      this.restartTimeout = null
      this.stop()
      this.start().catch(console.error)
    }, 2000)
  }

  stop(): void {
    console.log('Stopping WHEP client')

    if (this.restartTimeout !== null) {
      clearTimeout(this.restartTimeout)
      this.restartTimeout = null
    }

    if (this.pc) {
      this.pc.close()
      this.pc = null
    }

    if (this.videoElement.srcObject) {
      const stream = this.videoElement.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      this.videoElement.srcObject = null
    }
  }
}

