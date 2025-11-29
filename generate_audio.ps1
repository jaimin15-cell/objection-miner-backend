Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$outPath = Join-Path $PWD "test_speech.wav"
$synth.SetOutputToWaveFile($outPath)
$synth.Speak("Hello, I am calling to inquire about your software. I like the features but the cost is a bit expensive compared to your competitors.")
$synth.SetOutputToNull()
Write-Host "Audio file generated at $outPath"
