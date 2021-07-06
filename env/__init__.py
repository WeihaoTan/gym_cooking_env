from gym.envs.registration import register

register(
    id='Overcooked-v0',
    entry_point='env.overcooked:Overcooked',
)

register(
    id='Overcooked-MA-v0',
    entry_point='env.overcooked_MA:Overcooked_MA',
)