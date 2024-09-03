# ComfyUI Custom Nodes

A collection of custom nodes for ComfyUI.

## Nodes

### Cubemap to Spherical Map

Converts a 6-image cubemap input into a single equirectangular (spherical) map.

## Installation

1. Clone this repository into your ComfyUI `custom_nodes` folder:

	`git clone https://github.com/pixelprotest/ComfyUI-cozy-toolbelt`

2. Install the required dependencies:

	`pip install -r requirements.txt`

3. Restart ComfyUI or reload custom nodes.

## Usage

After installation, the new nodes will appear in the ComfyUI interface under their respective categories.

### Telegram Node

Set up your .env file with your Telegram bot token and chat ID.

To get your bot token and chat ID, you can use the Telegram BotFather.

`/mybots` to see your bots.
click `API Token` to get the Bot Token.
store it in the .env file as `TELEGRAM_BOT_TOKEN`.

then go to https://api.telegram.org/bot{api token here}/getUpdates 
send a message to your bot on telegram, 
then check the url above again and grab chat id from the response
then store it in the .env file as `TELEGRAM_CHAT_ID`.

NOTE you can put the .env file either in the root of the ComfyUI folder or in the root of this plugin folder e.g. `./custom_nodes/ComfyUI-cozy-toolbelt`


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
