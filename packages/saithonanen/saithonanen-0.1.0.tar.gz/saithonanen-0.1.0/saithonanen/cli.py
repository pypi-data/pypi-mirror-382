#!/usr/bin/env python3
"""
Saithonanen Command-Line Interface
Provides a user-friendly CLI for all major encryption and security features.
"""

import argparse
import getpass
import os
import sys

from .api import Saithonanen

def print_banner():
    """Prints the Saithonanen ASCII art banner."""
    banner = r"""
    ███████╗ █████╗ ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗ █████╗ ███╗   ██╗███╗   ██╗
    ██╔════╝██╔══██╗██║╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║██╔══██╗████╗  ██║████╗  ██║
    ███████╗███████║██║   ██║   ███████║██║   ██║██╔██╗ ██║███████║██╔██╗ ██║██╔██╗ ██║
    ╚════██║██╔══██║██║   ██║   ██╔══██║██║   ██║██║╚██╗██║██╔══██║██║╚██╗██║██║╚██╗██║
    ███████║██║  ██║██║   ██║   ██║  ██║╚██████╔╝██║ ╚████║██║  ██║██║ ╚████║██║ ╚████║
    ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝
    -- The Ultimate Encryption & Security Library --
    """
    print(banner)

def main():
    """Main function to run the CLI."""
    print_banner()
    parser = argparse.ArgumentParser(
        description="Saithonanen: The Ultimate Encryption & Security Library.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Symmetric Encryption --- #
    p_enc_sym = subparsers.add_parser("encrypt-sym", help="Encrypt a file symmetrically (with a password).")
    p_enc_sym.add_argument("-i", "--input", required=True, help="Input file path to encrypt.")
    p_enc_sym.add_argument("-o", "--output", required=True, help="Output file path for encrypted data.")
    p_enc_sym.add_argument("-p", "--password", help="Password for encryption. If not provided, you will be prompted.")

    # --- Symmetric Decryption --- #
    p_dec_sym = subparsers.add_parser("decrypt-sym", help="Decrypt a file symmetrically (with a password).")
    p_dec_sym.add_argument("-i", "--input", required=True, help="Input file path to decrypt.")
    p_dec_sym.add_argument("-o", "--output", required=True, help="Output file path for decrypted data.")
    p_dec_sym.add_argument("-p", "--password", help="Password for decryption. If not provided, you will be prompted.")

    # --- Asymmetric Key Generation --- #
    p_gen_keys = subparsers.add_parser("gen-keys-asym", help="Generate a new asymmetric key pair (public/private).")
    p_gen_keys.add_argument("--pub", required=True, help="Output path for the public key file.")
    p_gen_keys.add_argument("--priv", required=True, help="Output path for the private key file.")
    p_gen_keys.add_argument("-p", "--password", help="Optional password to encrypt the private key. If not provided, you will be prompted.")

    # --- Hybrid Encryption --- #
    p_enc_hybrid = subparsers.add_parser("encrypt-hybrid", help="Encrypt a file with a recipient's public key.")
    p_enc_hybrid.add_argument("-i", "--input", required=True, help="Input file path to encrypt.")
    p_enc_hybrid.add_argument("-o", "--output", required=True, help="Output file path for encrypted data.")
    p_enc_hybrid.add_argument("--pubkey", required=True, help="Path to the recipient's public key file.")

    # --- Hybrid Decryption --- #
    p_dec_hybrid = subparsers.add_parser("decrypt-hybrid", help="Decrypt a file with your private key.")
    p_dec_hybrid.add_argument("-i", "--input", required=True, help="Input file path to decrypt.")
    p_dec_hybrid.add_argument("-o", "--output", required=True, help="Output file path for decrypted data.")
    p_dec_hybrid.add_argument("--privkey", required=True, help="Path to your private key file.")
    p_dec_hybrid.add_argument("-p", "--password", help="Password for your private key. If not provided, you will be prompted.")

    # --- Steganography Hide --- #
    p_hide = subparsers.add_parser("hide", help="Hide a file inside a PNG image.")
    p_hide.add_argument("--secret-file", required=True, help="The file you want to hide.")
    p_hide.add_argument("--cover-image", required=True, help="The cover image (PNG, BMP, TIFF) to hide the file in.")
    p_hide.add_argument("-o", "--output", required=True, help="Output path for the new image with the hidden file.")
    p_hide.add_argument("-p", "--password", help="Password to encrypt the hidden file. If not provided, you will be prompted.")

    # --- Steganography Extract --- #
    p_extract = subparsers.add_parser("extract", help="Extract a hidden file from an image.")
    p_extract.add_argument("-i", "--input", required=True, help="The image containing the hidden file.")
    p_extract.add_argument("-o", "--output", required=True, help="Output path for the extracted secret file.")
    p_extract.add_argument("-p", "--password", help="Password to decrypt the hidden file. If not provided, you will be prompted.")

    args = parser.parse_args()
    api = Saithonanen()

    if args.command == "encrypt-sym":
        password = args.password or getpass.getpass("Enter encryption password: ")
        print("Encrypting file symmetrically...")
        api.encrypt_file_symmetric(args.input, args.output, password)
        print(f"File '{args.input}' encrypted to '{args.output}'.")

    elif args.command == "decrypt-sym":
        password = args.password or getpass.getpass("Enter decryption password: ")
        print("Decrypting file symmetrically...")
        api.decrypt_file_symmetric(args.input, args.output, password)
        print(f"File '{args.input}' decrypted to '{args.output}'.")

    elif args.command == "gen-keys-asym":
        password = args.password or getpass.getpass("Enter password to protect private key (or press Enter for none): ")
        password = password if password else None
        print("Generating asymmetric key pair...")
        priv_key, pub_key = api.asymmetric.generate_key_pair()
        priv_key_bytes = api.asymmetric.serialize_private_key(priv_key, password)
        pub_key_bytes = api.asymmetric.serialize_public_key(pub_key)
        with open(args.priv, "wb") as f:
            f.write(priv_key_bytes)
        with open(args.pub, "wb") as f:
            f.write(pub_key_bytes)
        print(f"Private key saved to '{args.priv}'.")
        print(f"Public key saved to '{args.pub}'.")

    elif args.command == "encrypt-hybrid":
        print("Encrypting file with hybrid encryption...")
        api.encrypt_file_hybrid(args.input, args.output, args.pubkey)
        print(f"File '{args.input}' encrypted to '{args.output}'.")

    elif args.command == "decrypt-hybrid":
        password = args.password or getpass.getpass("Enter private key password (or press Enter if none): ")
        password = password if password else None
        print("Decrypting file with hybrid encryption...")
        api.decrypt_file_hybrid(args.input, args.output, args.privkey, password)
        print(f"File '{args.input}' decrypted to '{args.output}'.")

    elif args.command == "hide":
        password = args.password or getpass.getpass("Enter password to encrypt the hidden file: ")
        print("Hiding file in image...")
        api.hide_file_in_image(args.secret_file, args.cover_image, args.output, password)
        print(f"File '{args.secret_file}' hidden in '{args.output}'.")

    elif args.command == "extract":
        password = args.password or getpass.getpass("Enter password to decrypt the hidden file: ")
        print("Extracting file from image...")
        api.extract_file_from_image(args.input, args.output, password)
        print(f"Extracted file saved to '{args.output}'.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

