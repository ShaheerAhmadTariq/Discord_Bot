const paymentOptions = {
    reply_markup: {
      inline_keyboard: [
        [
          {
            text: '🌸 Mini Tier 5$',
            url: 'https://buy.stripe.com/cN2cNL1kHedE4V24gu', // Replace with the URL for Option 1
          },
          {
            text: '🔥 Spark Tier 10$',
            url: 'https://buy.stripe.com/14keVT6F11qSgDK00d', // Replace with the URL for Option 2
          },
        ],
        [
          {
            text: '❤️ Classic Tier 15$',
            url: 'https://buy.stripe.com/9AQ6pn9Rd9Xo9bi4gv', // Replace with the URL for Option 2
          },
          {
            text: '💎 Pro Tiers 25$',
            url: 'https://buy.stripe.com/5kA6pn6F17Pg4V2dR2', // Replace with the URL for Option 2
          },
        ],
        [
          {
            text: '⭐ Ultimate Tier',
            url: 'https://buy.stripe.com/8wM297d3p3z0cnudR1', // Replace with the URL for Option 2
          },
        ],
      ],
    },
    parse_mode: 'HTML'
  };

  module.exports = paymentOptions