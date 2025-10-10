SignedID
===

Generate a short, opaque, url-safe, unique code whose provenance can be verified statelessly.

## Usage

The most basic usage looks like this:

```py
>>> import signed_id
>>> secret = 'shhhh!'
>>> signed_id.generate('my_unique_id', secret)
'e6bed2a1'
>>> signed_id.verify('e6bed2a1', secret)
True
```

## Overview

We need to be able to assign a unique code to a user that has the following properties:

 - The code is unique to a user
 - The code does not obviously reveal information about a user
 - We can verify that we generated the code
 - We do not need to store the code anywhere to verify it
 - The code is succinct for embedding in SMS messages
 - The code is a simple string, safe to pass in URLs
 - Valid codes are difficult to guess

## How it works

### Code generation

Codes are generated with, at minimum, an arbitrary piece of data about an entity and a secret string.

The specific steps are:

 1. Codes are generated from a unique piece of information about an entity, such as a database ID.
 2. This information is made opaque--while preserving uniqueness--with a strong hash function.
 3. The hash is truncated according to generation parameters to make the code more succinct.
 4. The hashed input is then signed by computing an additional hash with a secret piece of information.
 5. The signature hash is also truncated for succinctness.
 6. The two truncated hashes are concatenated, encoded as a hex string, and returned.

### Code verification

Verification works on the principle of proof-of-knowledge.
Nominally this means that the `secret` used for generation must also be known for verification.
In practice, the other generation parameters (hash function and byte lengths) also must be consistent across generation and validation.

The verification steps are:

 1. Decode the input from hex to a bytestring. If the input is not valid hex, verification fails.
 2. Parse the bytestring based on the byte length parameters to the input hash and the signature hash.
 3. Compute the expected signature hash based on the input hash, secret, and provided hash function.
 4. Truncate the expected signature based on the byte length parameter.
 5. Assert that the expected truncated signature matches the signature parsed from the code.

## Notes

### Code length

The code length is customizable, with the caveat that shorter codes have a higher risk for collision and guessability.

Codes contain exactly `id_bytes + sig_bytes` bytes of information.
Since the code bytes are represented as hex, the code length is `2 * (id_bytes + sig_bytes)`.

#### Defaults
By default we use `id_bytes=2, sig_bytes=2`, so the codes are 8-character ASCII strings. 

### Collisions
The probability of a collision (non-unique code generation) is `1 / 256^id_bytes`.

### Brute-forcing

The probability of generating a valid signature for a certain ID is `1 / 256^sig_bytes`.

The probability of generating a valid ID completely at random is correspondingly smaller.

### Reversing the input hash

The input hash is not inherently secure.
For example, if the input ID is a simple database ID,
and someone had access to a handful of codes,
it would not be difficult to infer the hash function and recover the input with a lookup table.
If it's necessary to guard against this, a more complicated (ideally salted) input should be used.
For example, instead of a database ID, use a composite input of the database ID and record creation time.

Even if the input hash is reversible, brute-forcing the signature would still often be impractical,
as it is effectively salted with the secret.