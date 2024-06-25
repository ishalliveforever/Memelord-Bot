# MemeLord Discord Bot

MemeLord is a Discord bot that allows users to submit memes and get rewarded with Bitcoin SV (BSV) when their memes receive 10 reactions. The bot tracks meme submissions, reactions, and handles payouts. Additionally, it awards badges for various milestones.

## Features

- **Meme Submission**: Users can submit memes by uploading an image.
- **Reaction Tracking**: The bot tracks reactions to memes and rewards users when their memes get 15 reactions.
- **Payouts**: Users receive 10,000 satoshis for each meme that reaches 10 reactions. Additional bonuses are awarded for earning badges.
- **Badges**: Users earn badges for submitting their first meme, earning 50,000 sats, and earning 100,000 sats.
- **Winning Meme Announcement**: Winning memes are posted in a designated channel with a congratulatory message.

## Requirements

- Python 3.7+
- Discord bot token
- Bitcoin SV wallet private key
- Environment variables for configuration

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/ishalliveforever/memelord.git
   cd memelord
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```env
   DISCORD_TOKEN=your-discord-bot-token
   WALLET_PRIVATE_KEY=your-wallet-private-key
   WINNING_CHANNEL_ID=your-channel-id
   PRIVATE_CHANNEL_ID=your-channel-id
   ```

## Usage

1. Run the bot:
   ```sh
   python meme.py
   ```

2. In Discord, use the command `/memelord` to submit a meme. Upload an image to complete the submission.

3. Users will be notified in the original channel when their meme reaches 10 reactions and wins 10,000 satoshis.

4. Winning memes will be posted in the specified channel with the message "This meme has been approved by 1Sat Society. Pump our bags!"

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.
```

### Final Steps

1. **Activate Virtual Environment**:

   If not already done, activate your virtual environment:
   ```sh
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Requirements**:

   Install the required Python packages listed in the `requirements.txt` file:
   ```sh
   pip install -r requirements.txt
   ```

3. **Create .env File**:

   Create a `.env` file in the root directory of your project with the following content:
   ```env
   DISCORD_TOKEN=your-discord-bot-token
   WALLET_PRIVATE_KEY=your-wallet-private-key
   WINNING_CHANNEL_ID=your-channel-id
   PRIVATE_CHANNEL_ID=your-channel-id
   ```

4. **Run the Bot**:

   Start the bot by running:
   ```sh
   python meme.py
   ```

### Explanation of Key Features

1. **Meme Submission**:
   - Users submit memes by typing `/memelord` and uploading an image.
   - The bot checks for valid image formats (png, jpg, jpeg, gif).

2. **Reaction Tracking**:
   - The bot tracks reactions to the submitted memes.
   - Users cannot add reactions to their own memes.
   - Each user can only add one reaction that counts towards the total.

3. **Payouts**:
   - When a meme receives 10 reactions, the user is awarded 10,000 satoshis.
   - A congratulatory message is sent in the original channel.

4. **Badges**:
   - Users earn badges based on their achievements:
     - **Normie Badge**: First meme submission.
     - **Based Memer**: Earned after accumulating 50,000 satoshis, along with a 50,000 sats bonus.
     - **Memelord**: Earned after accumulating 100,000 satoshis, along with a 100,000 sats bonus.

5. **Winning Meme Announcement**:
   - Winning memes are posted in a specified channel with the message "This meme has been approved by <your discord>. Pump our bags!"

By following these steps and understanding the features, you should have a fully functional MemeLord bot running in your Discord server.

Donate
## BSV: 1AehJyGHnPXMZ2zg4wdBjaowdLTebysFus
## BCH: qrxx9gycn3rrp6pd29p84ez2cceqc93gl5zdvttrjw
## BTC: bc1q5dc49up9k8ne90xn4n6edxd908n8het9maxwhu
## Doge: DJ1pkmDwdLS94ZSEJdVJoq2MHprDfjaUpZ
## Sol: 9HmpAhDoicGehmGhbbN5kmhsd5uZGm2DEDt68cGiUseJ

