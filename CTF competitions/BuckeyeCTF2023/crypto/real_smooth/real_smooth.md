# Crypto challenges
## Table of contents
- [Real Smooth (65 solves)](./crypto.md#real-smooth)

## Real Smooth
I know you're not supposed to leave passwords in plain text so I encrypted them.<br><br>
The flag is in the format `btcf`, not `bctf` due to a typo.<br>

### Solution
Let's unzip the archive to see what there is in there.<br>
We can find a [database.txt]() and a [main.py](). The database is the "encrypted" passwords as described in the challenge description, and the `main.py` script is how it has been encrypted.<br>
By checking this source code, we can find something interesting:
```py
def encrypt(key, nonce, plaintext):
    chacha = ChaCha20.new(key=key, nonce=nonce)
    return chacha.encrypt(plaintext)


def main():
    lines = open("passwords.txt", "rb").readlines()
    key = get_random_bytes(32)
    nonce = get_random_bytes(8)
    lines = [x.ljust(18) for x in lines]
    lines = [encrypt(key, nonce, x) for x in lines]
    open("database.txt", "wb").writelines(lines)
```
Don't see it? I will focus on one particular line:
```py
    lines = [encrypt(key, nonce, x) for x in lines]
```
Indeed, all of the lines in database are encrypted using the exact same key and nonce. This is our vulnerability. But how to exploit it?<br><br>
Chacha20 is a stream cipher. Thus, it uses a [One Time Pad](https://en.wikipedia.org/wiki/One-time_pad). Using the same key and nonce loses its confidentiality and allows us to discover plaintexts just by xoring them!<br>
But why? Here is the small math:<br>
We take $p_1$ as our first plaintext, $p_2$ as our second plaintext, $k$ as our common reused key, $c_1$ as our first plaintext and $c_2$ as our second plaintext.<br>
By One-Time Pad, we know that $c_1 = p_1 \oplus k$ and $c_2 = p_2 \oplus k$.<br>
But what happens if we try to XOR the two ciphertexts ?<br>
We get $c_1 \oplus c_2 = p_1 \oplus k \oplus p2 \oplus k = p_1 \oplus p_2 \oplus k \oplus k = p_1 \oplus p_2$<br>
We discover that xoring the two ciphertexts results in xoring the two plaintexts! But how do we use it?<br>
Well, if we know a bit of plaintext, imagine $p_1$, then we can xor it so we have $p_2$:<br>
$c_1 \oplus c_2 \oplus p_1 = p_1 \oplus p_1 \oplus p_2 = p_2$<br><br>
Now that we know the maths behind, let's use it on our challenge.<br>
We know a bit of plaintext, flag's format: `btcf{` (as mentionned in the description, flag format had a typo)<br>
But the database has 11431 entries, where is our flag??<br>
First, by looking a bit at the first 10 lines of the database:
```
c13c9abda3220824f2dc11e8510fc249ad48
c1229ab7b6350824f2dc11e8510fc249ad48
d32b84b2af20630ef2dc11e8510fc249ad48
cd2b87b4a3350824f2dc11e8510fc249ad48
cb2b90f6f47f0824f2dc11e8510fc249ad48
c52781a4ae7d3235d8dc11e8510fc249ad48
c43c9cb4b225636abd8e5ea6104386068748
c42191bef77e310ef2dc11e8510fc249ad48
cc2f99a2af2b6a0ef2dc11e8510fc249ad48
d42d9ab3b225670ef2dc11e8510fc249ad48
```
We can notice that every single flag ends by `48`. Why? Well, in the source code we see that all the entries are adjusted to have 18 characters. So 48 in this case might be the default adjust character: ` ` (space)<br>
So, I will do a script to discover if there are some entries that is not ending by 48, because I assume the flag has more than 18 characters:
```py
lines =  open("database.txt", "r").readlines()

soloLines = []
for line in lines:
    # Check if line doesn't finish with '48' but has a \n character at the end (last line finishes by 48 but has no \n character)
    if line[-3:-1] != '48' and line[-1] == '\n':
        soloLines.append(line[:-1])
print(soloLines)
```
This gives us two lines:
```py
['c53a96a1bd3b315bb6cc6efc2e43d35eba04', '94119ea9f63b6c5ba29005f91f18d111ba15']
```
Ok. So we know a potential ciphertext that is the beginning of the flag. Let's try to XOR the line `c53a96a1bd3b315bb6cc6efc2e43d35eba04` with the first line of the database, then xor it with our known plaintext `btcf{`
```py
from pwn import xor

...
# previous code
...

c1 = bytes.fromhex(soloLines[0])
c2 = bytes.fromhex(lines[0])
xored_ciphers = xor(c1, c2)
xorKnownPlaintext = xor(xored_ciphers, b'btcf{')

print(xorKnownPlaintext)
```
This gives us the output:
```py
b'froze{M\x1c"k\x1d`\x1c*juc/'
```
`froze` is something is personally recognize as a `rockyou.txt` password: `frozen`. If you are not sure like me, just grep it!
```bash
cat /opt/rockyou.txt| grep froze
```
```
Output:
frozen
frozenthrone
frozenfire
frozen1
...
```
Then, I began a long trial-and-error session to find the other bytes of the flag.<br>
First, I made my known plaintext 18 characters long by adding `0` to it: `btcf{0000000000000`<br>
This gave me
```py
b"froze)\tOt O$O|!''|"
```
Then, as I knew the character after `froze` was n, I changed the first `0` in my known plaintext to `n`.<br>
This gives me
```py
b"frozew\tOt O$O|!''|"
```
So the first byte is w. So know my plaintext is `btcf{w000000000000`<br>
I continued to test it on other lines but won't feature it in this writeup. I just discovered that every lines were in the form `password\n<spaces to 18 characters>`<br>
So, the first line is `frozen\n           `.
Let's XOR it to the `xored_ciphers`:
```py
xorKnownPlaintext = xor(xored_ciphers, b'frozen\n           ')
print(xorKnownPlaintext)
```
Output:
```py
b'btcf{w3_d0_4_l177l'
```
So.. that's not the end??<br>
Indeed not. But remember that we had TWO lines that didn't end with `48`.<br>
Let's try to use our brandly new known ciphertext to use on this second special line:
```py
c1 = bytes.fromhex(soloLines[0])
c2 = bytes.fromhex(soloLines[1])
xored_ciphers = xor(c1, c2)
xorKnownPlaintext = xor(xored_ciphers, b'btcf{w3_d0_4_l177l')
print(xorKnownPlaintext)
```
Output:
```py
b'3_kn0wn_pl41n73x7}'
```
And if we concatenate those two decrypted lines, we have the flag!<br>
*Note: You can find the [solve script here](./assets/scripts/real-smooth_solve.py) if you want to execute it and see how it works*
#### Flag
`btcf{w3_d0_4_l177l3_kn0wn_pl41n73x7}`
