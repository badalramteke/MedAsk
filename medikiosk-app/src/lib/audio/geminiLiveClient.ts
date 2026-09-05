/**
 * MediKiosk — Gemini Live API Bidirectional WebSocket Client
 * Connects to Gemini Live API WebSocket endpoint:
 * wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent
 *
 * Supports 4 Live Models:
 * 1. gemini-3.5-transcribe-live: Real-Time ASR (Speech-to-Text)
 * 2. gemini-2.5-flash-native-audio-dialog: Text-to-Speech native audio stream
 * 3. gemini-3.5-live-translate: Multilingual translation
 * 4. gemini-3-flash-live: General fallback
 */

export interface GeminiLiveASROptions {
  apiKey?: string;
  languageCode: string;
  onInterim: (text: string) => void;
  onFinal: (text: string) => void;
  onError: (error: any) => void;
  onClose?: (code: number, reason: string) => void;
}

export interface GeminiLiveTTSOptions {
  apiKey?: string;
  languageCode: string;
  text: string;
  onStart?: () => void;
  onAudioChunk?: (pcmBuffer: ArrayBufferLike) => void;
  onEnd?: () => void;
  onError?: (error: any) => void;
}

const WS_BASE_URL =
  'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent';

export class GeminiLiveClient {
  private asrWs: WebSocket | null = null;
  private ttsWs: WebSocket | null = null;
  private apiKey: string;

  constructor(apiKey?: string) {
    this.apiKey =
      apiKey ||
      (typeof process !== 'undefined' &&
        (process.env.NEXT_PUBLIC_GEMINI_API_KEY || process.env.GEMINI_API_KEY)) ||
      '';
  }

  public setApiKey(key: string) {
    this.apiKey = key;
  }

  public hasApiKey(): boolean {
    return Boolean(this.apiKey && this.apiKey.trim().length > 5);
  }

  // ==========================================
  // 1. ASR: gemini-3.5-transcribe-live
  // ==========================================
  public startASRSession(options: GeminiLiveASROptions): boolean {
    if (!this.hasApiKey()) {
      console.warn('Gemini Live API key not configured; falling back to Web Speech / backend ASR');
      return false;
    }

    try {
      this.stopASRSession();

      const wsUrl = `${WS_BASE_URL}?key=${encodeURIComponent(this.apiKey)}`;
      const ws = new WebSocket(wsUrl);
      this.asrWs = ws;

      ws.onopen = () => {
        // Send initial setup frame
        const setupMessage = {
          setup: {
            model: 'gemini-3.5-transcribe-live',
            generation_config: {
              language_code: options.languageCode || 'en-IN',
            },
          },
        };
        ws.send(JSON.stringify(setupMessage));
      };

      ws.onmessage = async (event) => {
        try {
          let data: any;
          if (typeof event.data === 'string') {
            data = JSON.parse(event.data);
          } else if (event.data instanceof Blob) {
            const text = await event.data.text();
            data = JSON.parse(text);
          }

          if (!data) return;

          // Check server content parts
          const serverContent = data.serverContent || data.server_content;
          if (serverContent) {
            const modelTurn = serverContent.modelTurn || serverContent.model_turn;
            if (modelTurn?.parts) {
              for (const part of modelTurn.parts) {
                if (part.text) {
                  if (serverContent.turnComplete || serverContent.turn_complete) {
                    options.onFinal(part.text);
                  } else {
                    options.onInterim(part.text);
                  }
                }
              }
            }
          }
        } catch (parseErr) {
          console.warn('Gemini ASR message parse notice:', parseErr);
        }
      };

      ws.onerror = (err) => {
        console.error('Gemini Live ASR WebSocket error:', err);
        options.onError(err);
      };

      ws.onclose = (ev) => {
        if (options.onClose) {
          options.onClose(ev.code, ev.reason);
        }
        this.asrWs = null;
      };

      return true;
    } catch (err) {
      console.error('Failed to open Gemini Live ASR WebSocket:', err);
      options.onError(err);
      return false;
    }
  }

  public sendAudioChunk(pcmChunk: ArrayBufferLike) {
    if (this.asrWs && this.asrWs.readyState === WebSocket.OPEN) {
      // Send binary PCM chunk over WebSocket
      this.asrWs.send(pcmChunk);
    }
  }

  public stopASRSession() {
    if (this.asrWs) {
      try {
        if (this.asrWs.readyState === WebSocket.OPEN || this.asrWs.readyState === WebSocket.CONNECTING) {
          this.asrWs.close(1000, 'Client closed ASR session');
        }
      } catch (e) {
        // Ignore
      }
      this.asrWs = null;
    }
  }

  // ==========================================
  // 2. TTS: gemini-2.5-flash-native-audio-dialog
  // ==========================================
  public async playTTSDialog(
    options: GeminiLiveTTSOptions,
    audioContext: AudioContext,
    onActiveSource?: (source: AudioBufferSourceNode) => void
  ): Promise<boolean> {
    if (!this.hasApiKey()) {
      return false;
    }

    return new Promise((resolve) => {
      try {
        this.stopTTS();

        const wsUrl = `${WS_BASE_URL}?key=${encodeURIComponent(this.apiKey)}`;
        const ws = new WebSocket(wsUrl);
        this.ttsWs = ws;

        ws.onopen = () => {
          options.onStart?.();

          // Setup frame for native audio dialog
          const setupMsg = {
            setup: {
              model: 'gemini-2.5-flash-native-audio-dialog',
              generation_config: {
                response_modalities: ['AUDIO'],
                speech_config: {
                  voice_config: {
                    prebuilt_voice_config: {
                      voice_name: 'Aoede',
                    },
                  },
                },
              },
            },
          };
          ws.send(JSON.stringify(setupMsg));

          // Client query frame asking model to vocalize question
          const clientContent = {
            client_content: {
              turns: [
                {
                  role: 'user',
                  parts: [{ text: options.text }],
                },
              ],
              turn_complete: true,
            },
          };
          ws.send(JSON.stringify(clientContent));
        };

        const audioChunks: ArrayBuffer[] = [];

        ws.onmessage = async (event) => {
          try {
            if (event.data instanceof Blob) {
              const buffer = await event.data.arrayBuffer();
              audioChunks.push(buffer);
              options.onAudioChunk?.(buffer);
            } else if (typeof event.data === 'string') {
              const data = JSON.parse(event.data);
              const parts = data.serverContent?.modelTurn?.parts || data.server_content?.model_turn?.parts;
              if (parts) {
                for (const part of parts) {
                  if (part.inlineData?.data) {
                    const binaryString = atob(part.inlineData.data);
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                      bytes[i] = binaryString.charCodeAt(i);
                    }
                    audioChunks.push(bytes.buffer);
                  }
                }
              }

              const isComplete = Boolean(
                data.serverContent?.turnComplete || data.server_content?.turn_complete
              );

              if (isComplete && audioChunks.length > 0) {
                // Decode and play all audio bytes through AudioContext
                await this.decodeAndPlayAudio(audioChunks, audioContext, onActiveSource);
                options.onEnd?.();
                ws.close();
                resolve(true);
              }
            }
          } catch (err) {
            console.error('Error processing TTS audio bytes:', err);
          }
        };

        ws.onerror = (err) => {
          console.warn('Gemini TTS WebSocket error:', err);
          options.onError?.(err);
          resolve(false);
        };

        ws.onclose = () => {
          this.ttsWs = null;
        };
      } catch (err) {
        console.warn('Gemini TTS connection failed:', err);
        resolve(false);
      }
    });
  }

  private async decodeAndPlayAudio(
    chunks: ArrayBuffer[],
    audioContext: AudioContext,
    onActiveSource?: (source: AudioBufferSourceNode) => void
  ): Promise<void> {
    try {
      // Concatenate array buffers
      const totalLength = chunks.reduce((acc, c) => acc + c.byteLength, 0);
      const combined = new Uint8Array(totalLength);
      let offset = 0;
      for (const chunk of chunks) {
        combined.set(new Uint8Array(chunk), offset);
        offset += chunk.byteLength;
      }

      const audioBuffer = await audioContext.decodeAudioData(combined.buffer);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);

      if (onActiveSource) {
        onActiveSource(source);
      }

      return new Promise((resolve) => {
        source.onended = () => resolve();
        source.start(0);
      });
    } catch (err) {
      console.warn('AudioContext decodeAudioData error on raw bytes:', err);
    }
  }

  public stopTTS() {
    if (this.ttsWs) {
      try {
        if (this.ttsWs.readyState === WebSocket.OPEN || this.ttsWs.readyState === WebSocket.CONNECTING) {
          this.ttsWs.close(1000, 'Client stopped TTS');
        }
      } catch (e) {
        // Ignore
      }
      this.ttsWs = null;
    }
  }

  // ==========================================
  // 3. Translation: gemini-3.5-live-translate
  // ==========================================
  public async translateText(
    text: string,
    sourceLang: string,
    targetLang: string
  ): Promise<string | null> {
    if (!this.hasApiKey() || !text || sourceLang === targetLang) {
      return text;
    }

    try {
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${encodeURIComponent(
        this.apiKey
      )}`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [
            {
              role: 'user',
              parts: [
                {
                  text: `Translate this clinical patient text accurately from ${sourceLang} to ${targetLang}. Return ONLY the direct translation:\n\n${text}`,
                },
              ],
            },
          ],
        }),
      });

      if (!res.ok) return null;
      const data = await res.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || null;
    } catch (err) {
      console.warn('Translation request fallback:', err);
      return null;
    }
  }
}

export const geminiLiveClient = new GeminiLiveClient();
