const { commands, paymentOptions, botDescription } = require("./constants");
const {
  sendTextToApi,
  sendVoiceToApi,
  userInfo,
  sendBalanceCommandToApi,
  sendClearCommandToApi,
} = require("./helpers");
const telegramBot = require("node-telegram-bot-api");
require("dotenv").config();
const ffmpeg = require("fluent-ffmpeg");
const axios = require("axios");
const stream = require("stream");
const fs = require("fs");

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

bot.onText(/\/deposit/, (message) => {
  const { chatId, userId, username } = userInfo(message);
  const description = `Payments are securely powered by Stripe. Before Depositing amount these are your informations.\n<b>User Name: @${username}\nUser ID: ${userId}</b>`;

  bot.sendMessage(chatId, description, paymentOptions);
});

bot.onText(/\/clear/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message
  const { chatId } = userInfo(message);

  const description = `history removed`;
  await sendClearCommandToApi(userId, username);

  bot.sendMessage(chatId, description);
});

bot.onText(/\/balance/, async (message) => {
  // 'msg' is the received Message from Telegram
  // 'match' is the result of executing the regexp above on the text content
  // of the message
  const { userId, username } = userInfo(message);

  const balance = await sendBalanceCommandToApi(userId, username);
  const description = `Your current Balance is ${balance}`;

  bot.sendMessage(chatId, description);
});

bot.on("voice", async (message) => {
  try {
    console.log(message);
    const voiceId = message.voice.file_id;
    const { chatId, userId, username } = userInfo(message);

    const oggAudioUrl = `${process.env.TELEGRAM_API_LINK}${Token}/${voiceId}`;
    const oggFileName = `${username}${Date.now()}.ogg`;
    fs.writeFileSync(`../${oggFileName}`, oggAudioUrl);

    const response = await sendVoiceToApi(oggFileName, userId, username);
    bot.sendMessage(chatId, response);
  } catch (err) {
    console.error(err.message);
  }
});

bot.on("text", async (message) => {
  const { chatId, userId, username } = userInfo(message);
  // Check if the message starts with the bot's prefix or is a slash command
  if (message.text.startsWith("/")) {
    console.log("worked");
    return; // Ignore messages with commands
  }

  const response = await sendTextToApi(message.text, userId, username);
  bot.sendMessage(chatId, response);
  // Your bot's logic for responding to regular messages goes here
  // For example, you can reply with a message:

  // Or perform any other actions based on the message content
});
