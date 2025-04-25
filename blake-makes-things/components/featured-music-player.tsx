"use client"

import { useState, useRef, useEffect } from "react"
import Image from "next/image"
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from "lucide-react"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

// Featured tracks data
const featuredTracks = [
  {
    id: "track-1",
    title: "Midnight Echoes",
    description: "Ambient electronic with layered synths",
    coverImage: "/sonic-abstraction.png",
    audioSrc: "https://example.com/track1.mp3", // Replace with actual audio URL
    duration: "3:45",
    genre: "Electronic",
  },
  {
    id: "track-2",
    title: "Urban Reflections",
    description: "Hip-hop instrumental with jazz influences",
    coverImage: "/rhythmic-cityscape.png",
    audioSrc: "https://example.com/track2.mp3", // Replace with actual audio URL
    duration: "4:12",
    genre: "Hip-Hop",
  },
  {
    id: "track-3",
    title: "Digital Dreams",
    description: "Experimental electronic with glitchy beats",
    coverImage: "/sonic-spectrum.png",
    audioSrc: "https://example.com/track3.mp3", // Replace with actual audio URL
    duration: "5:30",
    genre: "Experimental",
  },
  {
    id: "track-4",
    title: "Sunset Boulevard",
    description: "Chill lo-fi beat with warm analog textures",
    coverImage: "/sunset-soundscape.png",
    audioSrc: "https://example.com/track4.mp3", // Replace with actual audio URL
    duration: "3:18",
    genre: "Lo-Fi",
  },
  {
    id: "track-5",
    title: "Neural Network",
    description: "Futuristic techno with complex rhythms",
    coverImage: "/sonic-cityscape.png",
    audioSrc: "https://example.com/track5.mp3", // Replace with actual audio URL
    duration: "6:24",
    genre: "Techno",
  },
]

export function FeaturedMusicPlayer() {
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(80)
  const [isMuted, setIsMuted] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const previousVolume = useRef(volume)

  const currentTrack = featuredTracks[currentTrackIndex]

  useEffect(() => {
    if (audioRef.current) {
      const audio = audioRef.current

      const handleTimeUpdate = () => {
        if (audio.duration) {
          setProgress((audio.currentTime / audio.duration) * 100)
        }
      }

      const handleLoadedMetadata = () => {
        setDuration(audio.duration)
      }

      const handleEnded = () => {
        handleNext()
      }

      audio.addEventListener("timeupdate", handleTimeUpdate)
      audio.addEventListener("loadedmetadata", handleLoadedMetadata)
      audio.addEventListener("ended", handleEnded)

      return () => {
        audio.removeEventListener("timeupdate", handleTimeUpdate)
        audio.removeEventListener("loadedmetadata", handleLoadedMetadata)
        audio.removeEventListener("ended", handleEnded)
      }
    }
  }, [currentTrackIndex])

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch((error) => {
          console.error("Error playing audio:", error)
          setIsPlaying(false)
        })
      } else {
        audioRef.current.pause()
      }
    }
  }, [isPlaying, currentTrackIndex])

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume / 100
    }
  }, [volume, isMuted])

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handlePrevious = () => {
    setCurrentTrackIndex((prev) => (prev === 0 ? featuredTracks.length - 1 : prev - 1))
    if (isPlaying) {
      setIsPlaying(false)
      setTimeout(() => setIsPlaying(true), 100)
    }
  }

  const handleNext = () => {
    setCurrentTrackIndex((prev) => (prev === featuredTracks.length - 1 ? 0 : prev + 1))
    if (isPlaying) {
      setIsPlaying(false)
      setTimeout(() => setIsPlaying(true), 100)
    }
  }

  const handleProgressChange = (newValue: number[]) => {
    if (audioRef.current && duration) {
      const newTime = (newValue[0] / 100) * duration
      audioRef.current.currentTime = newTime
      setProgress(newValue[0])
    }
  }

  const handleVolumeChange = (newValue: number[]) => {
    const newVolume = newValue[0]
    setVolume(newVolume)
    previousVolume.current = newVolume
    setIsMuted(newVolume === 0)
  }

  const toggleMute = () => {
    if (isMuted) {
      setVolume(previousVolume.current)
      setIsMuted(false)
    } else {
      previousVolume.current = volume
      setVolume(0)
      setIsMuted(true)
    }
  }

  const formatTime = (time: number) => {
    if (!time) return "0:00"
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  const selectTrack = (index: number) => {
    setCurrentTrackIndex(index)
    setIsPlaying(true)
  }

  return (
    <div className="space-y-8">
      <audio ref={audioRef} src={currentTrack.audioSrc} preload="metadata" onEnded={() => handleNext()} />

      {/* Main Player */}
      <div className="relative rounded-xl border border-purple-500/20 bg-zinc-900/70 p-6 backdrop-blur-sm">
        <div className="grid gap-6 md:grid-cols-[300px_1fr]">
          {/* Album Art */}
          <div className="relative aspect-square overflow-hidden rounded-lg border border-zinc-800">
            <Image
              src={currentTrack.coverImage || "/placeholder.svg"}
              alt={currentTrack.title}
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity hover:opacity-100">
              <Button
                variant="outline"
                size="icon"
                className="h-16 w-16 rounded-full border-purple-500/50 bg-purple-500/20 text-white hover:bg-purple-500/30"
                onClick={handlePlayPause}
              >
                {isPlaying ? <Pause className="h-8 w-8" /> : <Play className="h-8 w-8" />}
              </Button>
            </div>
          </div>

          {/* Player Controls */}
          <div className="flex flex-col justify-between">
            <div>
              <Badge className="mb-2 bg-purple-500/20 text-purple-300">{currentTrack.genre}</Badge>
              <h3 className="text-2xl font-bold text-white">{currentTrack.title}</h3>
              <p className="mt-1 text-zinc-400">{currentTrack.description}</p>
            </div>

            <div className="mt-6 space-y-4">
              {/* Progress Bar */}
              <div className="space-y-2">
                <Slider
                  value={[progress]}
                  max={100}
                  step={0.1}
                  onValueChange={(newValue) => handleProgressChange(newValue)}
                  className="cursor-pointer"
                />
                <div className="flex justify-between text-xs text-zinc-500">
                  <span>{audioRef.current ? formatTime(audioRef.current.currentTime) : "0:00"}</span>
                  <span>{currentTrack.duration}</span>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" onClick={toggleMute} className="text-zinc-400 hover:text-white">
                    {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                  </Button>
                  <div className="w-24">
                    <Slider
                      value={[volume]}
                      max={100}
                      step={1}
                      onValueChange={handleVolumeChange}
                      className="cursor-pointer"
                    />
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handlePrevious}
                    className="h-10 w-10 rounded-full text-zinc-400 hover:bg-purple-500/10 hover:text-white"
                  >
                    <SkipBack className="h-5 w-5" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handlePlayPause}
                    className="h-14 w-14 rounded-full border-purple-500/50 bg-purple-500/10 text-white hover:bg-purple-500/20"
                  >
                    {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleNext}
                    className="h-10 w-10 rounded-full text-zinc-400 hover:bg-purple-500/10 hover:text-white"
                  >
                    <SkipForward className="h-5 w-5" />
                  </Button>
                </div>
                <div className="w-[88px]"></div> {/* Spacer to balance the layout */}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Track Carousel */}
      <ScrollArea className="w-full pb-4">
        <div className="flex space-x-4 pb-4">
          {featuredTracks.map((track, index) => (
            <motion.div
              key={track.id}
              whileHover={{ y: -5 }}
              transition={{ duration: 0.3 }}
              className={`w-[200px] flex-shrink-0 cursor-pointer rounded-lg border ${
                currentTrackIndex === index
                  ? "border-purple-500/50 bg-purple-500/10"
                  : "border-zinc-800 bg-zinc-900/50 hover:border-purple-500/30"
              } p-4 transition-colors`}
              onClick={() => selectTrack(index)}
            >
              <div className="relative aspect-square overflow-hidden rounded-md">
                <Image
                  src={track.coverImage || "/placeholder.svg"}
                  alt={track.title}
                  fill
                  className="object-cover transition-transform duration-300 hover:scale-105"
                />
                {currentTrackIndex === index && isPlaying && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                    <div className="flex space-x-1">
                      <span className="h-8 w-1.5 animate-pulse rounded-full bg-purple-500"></span>
                      <span
                        className="h-8 w-1.5 animate-pulse rounded-full bg-purple-500"
                        style={{ animationDelay: "0.2s" }}
                      ></span>
                      <span
                        className="h-8 w-1.5 animate-pulse rounded-full bg-purple-500"
                        style={{ animationDelay: "0.4s" }}
                      ></span>
                    </div>
                  </div>
                )}
              </div>
              <div className="mt-3">
                <h4 className="line-clamp-1 font-medium text-white">{track.title}</h4>
                <p className="line-clamp-1 text-xs text-zinc-400">
                  {track.genre} • {track.duration}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}
