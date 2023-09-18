const telegramBot = require("node-telegram-bot-api");
require("dotenv").config();
const ffmpeg = require('fluent-ffmpeg');
const axios = require('axios');
const stream = require('stream');

const Token = process.env.TELEGRAM_TOKEN;
const bot = new telegramBot(Token, { polling: true });

bot.on('text', (message) => {
  console.log(message);
  bot.sendMessage(message.from.id, "Yo, what's up bro");
});

bot.onText(/\/echo (.+)/,(msg, match) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message

  const chatId = msg.chat.id;
  const resp = match[1]; // the captured "whatever"

  // send back the matched "whatever" to the chat
  bot.sendMessage(chatId, resp);
})

bot.setMyCommands([
  { command: "start", description: "إبدأ من جديد" },
  { command: "help", description: "طلب مساعدة " },
  { command: "list", description: "القائمة " },
  ])


bot.on('voice', async (message) => {
  try {
    const voiceId = message.voice.file_id;

    // Download the OGG audio file using the bot's getFile method
    const oggAudioFile = await bot.getFile(voiceId);

    // Construct the URL to download the file
    const oggAudioUrl = `https://api.telegram.org/file/bot${Token}/${oggAudioFile.file_path}`;

    // Create a PassThrough stream for the converted WAV audio
    const wavAudioStream = ffmpeg()
      .input(oggAudioUrl)
      .audioCodec('pcm_s16le') // Set the audio codec to WAV
      .toFormat('wav')
      .pipe();

    // Convert the PassThrough stream to a Node.js Readable Stream
    const wavReadableStream = new stream.PassThrough();
    wavAudioStream.pipe(wavReadableStream);

    // Read the WAV audio data and send it to your API endpoint as base64
    let wavAudioData = '';
    wavReadableStream.on('data', (chunk) => {
      wavAudioData += chunk.toString('base64');
    });

    wavReadableStream.on('end', () => {
      // Send the WAV audio data to your API endpoint
      sendWavToApi(wavAudioData);
    });
    
  } catch (err) {
    console.error(err.message);
  }
});

function sendWavToApi(wavAudioData) {
  // Use axios to send the audio data directly to your API
  axios.post("http://localhost:1000/upload-wav", { audioData: wavAudioData })
    .then((response) => {
      console.log('Response from API:', response.data);
    })
    .catch((error) => {
      console.error('Error sending audio data to the API:', error);
    });
}
