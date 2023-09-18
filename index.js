const telegramBot = require("node-telegram-bot-api");
require("dotenv").config();
const ffmpeg = require('fluent-ffmpeg');
const axios = require('axios');
const stream = require('stream');
const fs = require('fs');

const Token = process.env.TELEGRAM_TOKEN;
const bot = new telegramBot(Token, { polling: true });

// bot.on('text', (message) => {
//   console.log(message);
//   bot.sendMessage(message.from.id, "Yo, what's up bro");
// });

// bot.onText(/\/echo (.+)/,(msg, match) => {
//   // 'msg' is the received Message from Telegram
//   // 'match' is the result of executing the regexp above on the text content
//   // of the message

//   const chatId = msg.chat.id;
//   const resp = match[1]; // the captured "whatever"

//   // send back the matched "whatever" to the chat
//   bot.sendMessage(chatId, resp);
// })

bot.setMyCommands([
  { command: "start", description: "إبدأ من جديد" },
  { command: "help", description: "طلب مساعدة " },
  { command: "list", description: "القائمة " },
  ])


bot.on('voice', async (message) => {
  try {
    console.log(message)
    const voiceId = message.voice.file_id;
    const username = message.from.username;
    const userId = message.from.id
    const chatId = message.chat.id

    const oggAudioUrl = `https://api.telegram.org/file/bot${Token}/${voiceId}`;
    const oggFileName = `${username}${Date.now()}.ogg`
    fs.writeFileSync( `../${oggFileName}`, oggAudioUrl);
    
    const response= await sendVoiceToApi(oggFileName, userId, username);
    bot.sendMessage(chatId,response)
    
  } catch (err) {
    console.error(err.message);
  }
});





bot.on('text', async(message) => {

  const username = message.from.username;
    const userId = message.from.id
    const chatId = message.chat.id

  console.log(message)
  // Check if the message starts with the bot's prefix or is a slash command
  if ( message.text.startsWith('/')) {
    console.log("worked")
    return; // Ignore messages with commands
  }

  const response= await sendTextToApi(message.text, userId, username);
  bot.sendMessage(chatId,response)
  // Your bot's logic for responding to regular messages goes here
  // For example, you can reply with a message:
  

  // Or perform any other actions based on the message content
});


async function sendTextToApi(message, userId, username) {
  try{

    const response =await axios.post("https://3b32-139-135-45-18.ngrok-free.app/generate_response_llm", { message: message, user_id: userId.toString(), user_name: username  })
    return (response.data.message)
  } catch(err){
    console.error('Error sending audio data to the API:', err)

  }
  // Use axios to send the audio data directly to your API
 
}

async function sendVoiceToApi(filePath, userId, username) {
  try{

    const response =await axios.post("https://3b32-139-135-45-18.ngrok-free.app/generate_response_llm_audio", { audio_file_path: filePath, user_id: userId.toString(), user_name: username  })
    return (response.data.message)
  } catch(err){
    console.error('Error sending audio data to the API:', err)

  }
  // Use axios to send the audio data directly to your API
 
}
