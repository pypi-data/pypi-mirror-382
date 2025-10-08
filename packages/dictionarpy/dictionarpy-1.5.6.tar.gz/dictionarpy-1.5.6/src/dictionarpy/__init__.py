import argparse
from dictionarpy.dictionarpy import DictionarPy


def main():
    parser = argparse.ArgumentParser(description='Offline dictionary')
    parser.add_argument('word', nargs='?', help='Word to be defined') 
    parser.add_argument('-n', '--no-ansi', action='store_true', 
        help="Don't use ansi escape sequences")
    parser.add_argument('-e', '--no-stemming', action='store_true', 
        help="Don't use Porter Stemming on a word if it's not found")
    parser.add_argument('-s', '--stats', action='store_true', 
        help='Show database statistics')
    parser.add_argument('-t', '--tail', type=int, metavar='N',
        help='Show last N words added to the database')
    parser.add_argument('-g', '--ipa-guide', const='all', metavar='IPA SYMBOL',
        nargs='?', help='Show ipa guide (empty for all)')
    parser.add_argument('-z', '--random', const='any', nargs='?', 
        metavar='PART OF SPEECH', help='Return a random word')
    parser.add_argument('-r', '--remove-def', type=int, metavar='INDEX',
        help='Remove a definition specified by its index')
    parser.add_argument('-R', '--remove-word', action='store_true',
        help='Remove a word')
    parser.add_argument('-f', '--find-in-defs', type=str, metavar='STRING',
        help='Show entries which contain STRING in definitions')
    parser.add_argument('-a', '--add', action='store_true',
        help='Add new entry to the dictionary (used with -w [[-p -d] -i])')
    parser.add_argument('-w', '--addword', type=str, 
        help='Word to add/word to add to')
    parser.add_argument('-p', '--pos', type=str, help='Part of speech to add')
    parser.add_argument('-d', '--definition', type=str, 
        help='Definition to add')
    parser.add_argument('-i', '--ipa', type=str, help='Pronunciation to add')
    parser.add_argument('-V', '--version', action='store_true', 
        help='Show version')
    args = parser.parse_args()

    if args.stats:
        DictionarPy('', args.no_ansi, args.no_stemming).show_stats()
    elif args.version:
        DictionarPy('', args.no_ansi, args.no_stemming).show_versions()
    elif args.ipa_guide:
        DictionarPy('', args.no_ansi, args.no_stemming
                    ).show_ipa_guide(args.ipa_guide)
    elif args.tail:
        DictionarPy('', args.no_ansi, args.no_stemming
                    ).show_recent_words(args.tail)
    elif args.random:
        DictionarPy('', args.no_ansi, args.no_stemming
                    ).show_random_word(args.random)
    elif args.remove_def:
        if args.word is None:
            parser.error(
                'The -r/--remove flag requires a word to be specified.')
        with DictionarPy(args.word, args.no_ansi, args.no_stemming) as dpy:
            dpy.remove_definition(args.remove_def)
    elif args.remove_word:
        with DictionarPy(args.word, args.no_ansi, args.no_stemming) as dpy:
            dpy.remove_word()
    elif args.find_in_defs:
        with DictionarPy('', args.no_ansi, args.no_stemming) as dpy:
            dpy.find_in_definitions(args.find_in_defs)
    elif args.add and args.addword:
        if bool(args.pos) ^ bool(args.definition):
            parser.error('The -p and -d flags are mutually dependent.')
        with DictionarPy('', args.no_ansi, args.no_stemming) as dpy:
            dpy.add_or_update_entry(
                args.addword, args.pos, args.definition, args.ipa)
    elif args.word is None:
        parser.print_help()
    else:
        with DictionarPy(args.word, args.no_ansi, args.no_stemming) as dpy:
            dpy.show_definitions()
