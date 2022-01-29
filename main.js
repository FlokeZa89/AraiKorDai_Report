const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { Client, Intents , MessageEmbed} = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS] });
const { clientId, guildId, token } = require('./auth.json');

const commands = [
	new SlashCommandBuilder().setName('ping').setDescription('Replies with pong!'),
	new SlashCommandBuilder().setName('server').setDescription('Replies with server info!'),
	new SlashCommandBuilder().setName('botinfo').setDescription('Checking botinfo!'),
]
	.map(command => command.toJSON());

const rest = new REST({ version: '9' }).setToken(token);

rest.put(Routes.applicationGuildCommands(clientId, guildId), { body: commands })
	.then(() => console.log('Successfully registered application commands!'))
	.catch(console.error);

    client.once('ready', () => {
        console.log('Ready!');
    });
    
    client.on('interactionCreate', async interaction => {
        if (!interaction.isCommand()) return;
    
        const { commandName } = interaction;
    
        if (commandName === 'ping') {
            await interaction.reply('Pong!');
        } else if (commandName === 'server') {
            await interaction.reply('Server info.');
        } else if (commandName === 'botinfo') {
            
            const info = new MessageEmbed()
                .setTitle("ข้อมูลเกี่ยวกับบอท")
                .setColor(0x00AE86)
                .setDescription("ดูข้อมูลเพิ่มเติมได้ที่ Github นะ! ")
	            .addFields(
	            	{ name: 'เวอร์ชั่นบอท : ', value: 'b163829012565' },
	            	{ name: 'Github', value: 'https://github.com/FlokeZa89/AraiKorDai' },
	            )
                .setFooter("@Araikordai Project")
	            .setTimestamp()
	            
            await interaction.reply({embeds: [info] });
        }
    });
    
    client.login(token);