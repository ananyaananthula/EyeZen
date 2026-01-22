setInterval(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(data => {
        console.log('Blink Count:', data.blinks)
        console.log('Blink Rate (BPM):', data.bpm)
      });
  }, 5000); // every 5 seconds
  