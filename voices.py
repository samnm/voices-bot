import discord
import argparse

INSTIGATOR_NAME='New Session'
GENERATED_PREFIX='#'
GENERATED_NAME='{}{}'

class VoicesBot(discord.Client):
    async def on_ready(self):
        self.instigator_channels = {}

        for guild in self.guilds:
            channel = self.instigator_channel(guild)
            if not channel:
                channel = await guild.create_voice_channel(INSTIGATOR_NAME)
            self.instigator_channels[guild] = channel

        print('Logged on as {0}!'.format(self.user))

    async def on_voice_state_update(self, member, before, after):
        if before.channel:
            guild = before.channel.guild

            if before.channel.name.startswith(GENERATED_PREFIX) and len(before.channel.members) == 0:
                await self.remove_channel(before.channel)

        if after.channel:
            guild = after.channel.guild

            if after.channel == self.instigator_channel(guild):
                new_channel = await self.create_next_channel(guild)
                for member in after.channel.members:
                    await member.move_to(new_channel)

    async def create_next_channel(self, guild):
        inst = self.instigator_channel(guild)
        name = GENERATED_NAME.format(GENERATED_PREFIX, self.num_channels(guild) + 1)
        return await inst.clone(name=name)

    async def remove_channel(self, channel):
        guild = channel.guild
        await channel.delete()
        self.rename_channels(guild)

    def rename_channels(self, guild):
        i = 0
        for channel in guild.voice_channels:
            if channel.name.startswith(GENERATED_PREFIX) and len(channel.members) > 0:
                i += 1
                channel.name = GENERATED_NAME.format(GENERATED_PREFIX, i)

    def instigator_channel(self, guild):
        if guild in self.instigator_channels:
            return self.instigator_channels[guild]

        for channel in guild.voice_channels:
            if channel.name == INSTIGATOR_NAME:
                return channel

        return None

    def num_channels(self, guild):
        count = 0
        for channel in guild.voice_channels:
            if channel.name.startswith(GENERATED_PREFIX):
                count += 1
        return count



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automatically manage discord voice channels.')
    parser.add_argument('client_id', help='discord client id')
    args = parser.parse_args()

    client = VoicesBot()
    client.run(args.client_id)
