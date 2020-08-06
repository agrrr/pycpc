import pandas as pd
import numpy as np
def bit_i_flipped_given_i_numbitflips(n):
    return pd.DataFrame(data=np.array([np.full_like(np.arange(n, dtype=float), (bitflips/n)) for bitflips in range(0, n+1)]), 
                        index=pd.Index(range(0, n+1), name='#bitflips'),
                        columns=pd.Index(range(0, n), name='bit'))