const { commands, paymentOptions, botDescription } = require("./constants");
const {
  sendTextToApi,
  sendVoiceToApi,
  userInfo,
  sendBalanceCommandToApi,
  sendClearCommandToApi,
  sendTextCommandToApi,
  sendAudioCommandToApi,
} = require("./helpers");
const telegramBot = require("node-telegram-bot-api");
require("dotenv").config();
const fs = require("fs");
const ffmpeg = require("fluent-ffmpeg");
const stream = require("stream");
const axios = require("axios");

const Token = process.env.TELEGRAM_TOKEN;
const bot = new telegramBot(Token, { polling: true });

bot.setMyCommands(commands);

bot.onText(/\/guide/, (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message

  const { chatId } = userInfo(message);
  // send back the matched "whatever" to the chat
  console.log(message.from.id);
  bot.sendMessage(chatId, botDescription, { parse_mode: "Markdown" });
});

bot.onText(/\/text/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message

  const { chatId, userId } = userInfo(message);
  // send back the matched "whatever" to the chat
  await sendTextCommandToApi(userId);
  console.log(message);
  bot.sendMessage(chatId, "You will receive text messages onwards.", {
    parse_mode: "Markdown",
  });
});

bot.onText(/\/audio/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message

  const { chatId, userId } = userInfo(message);
  // send back the matched "whatever" to the chat
  await sendAudioCommandToApi(userId);
  bot.sendMessage(chatId, "You will receive audio messages onwards.", {
    parse_mode: "Markdown",
  });
});

bot.onText(/\/deposit/, (message) => {
  const { chatId, userId, username } = userInfo(message);
  const description = `Payments are securely powered by Stripe. Before Depositing amount these are your informations.\n<b>User Name: @${username}\nUser ID: ${userId}</b>`;

  bot.sendMessage(chatId, description, paymentOptions);
});

bot.onText(/\/clear/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message
  const { userId, chatId } = userInfo(message);

  const response = await sendClearCommandToApi(userId);
  if (response) {
    bot.sendMessage(chatId, `History removed!`);
  } else {
    bot.sendMessage(chatId, `Something went wrong!`);
  }
});

bot.onText(/\/balance/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message
  const { userId, chatId } = userInfo(message);

  const balance = await sendBalanceCommandToApi(userId);
  const description = `Your current Balance is ${balance}$`;

  bot.sendMessage(chatId, description);
});

bot.on("voice", async (message) => {
  try {
    const voiceId = message.voice.file_id;
    const { chatId, userId, username } = userInfo(message);
    const oggAudioFile = await bot.getFile(voiceId);
    const oggAudioUrl = `${process.env.TELEGRAM_API_LINK}${Token}/${oggAudioFile.file_path}`;
    const wavFileName = `${username}${Date.now()}.wav`;

    const oggAudioResponse = await axios.get(oggAudioUrl, {
      responseType: "arraybuffer",
    });

    // Encode the OGG audio file as base64
    const base64Data = Buffer.from(oggAudioResponse.data).toString("base64");
    // Send the WAV audio data to your API endpoint
    const { is_audio, reply } = await sendVoiceToApi(
      base64Data,
      userId,
      username
    );

    // const { is_audio, reply } = await sendVoiceToApi(
    //   wavAudioData,
    //   userId,
    //   username
    // );
    console.log(is_audio);
    console.log(reply);
    if (is_audio) {
      const path = `../../Discord_Bot-dev-server/${reply}`;
      const audio = fs.readFileSync(path);
      bot.sendVoice(chatId, audio, {
        reply_to_message_id: message.message_id, // Optional: To make it a reply
      });
      fs.unlink(path, (err) => {
        if (err) {
          console.error(`Error deleting file: ${err}`);
        } else {
          console.log(`File ${reply} has been deleted successfully.`);
        }
      });
    } else {
      bot.sendMessage(chatId, reply, {
        reply_to_message_id: message.message_id,
      });
    }
  } catch (err) {
    console.error(err.message);
  }
});

bot.on("text", async (message) => {
  try {
    const { chatId, userId, username } = userInfo(message);
    // Check if the message starts with the bot's prefix or is a slash command
    if (message.text.startsWith("/")) {
      console.log("worked");
      return; // Ignore messages with commands
    }

    const { is_audio, reply } = await sendTextToApi(
      message.text,
      userId,
      username
    );
    if (is_audio) {
      const path = `../../Discord_Bot-dev-server/${reply}`;
      const audio = fs.readFileSync(path);
      bot.sendVoice(chatId, audio, {
        reply_to_message_id: message.message_id, // Optional: To make it a reply
      });
      fs.unlink(path, (err) => {
        if (err) {
          console.error(`Error deleting file: ${err}`);
        } else {
          console.log(`File ${reply} has been deleted successfully.`);
        }
      });
    } else {
      bot.sendMessage(chatId, reply, {
        reply_to_message_id: message.message_id,
      });
    }

    // Your bot's logic for responding to regular messages goes here
    // For example, you can reply with a message:

    // Or perform any other actions based on the message content
  } catch (err) {
    console.error(err.message);
  }
});
