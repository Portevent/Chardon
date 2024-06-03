import logging

from .raw_doc import RawDoc


# Open a file and return a list of RawDoc (/// paragraph with their associated function / class declaration)
def extract_doc_from(file) -> list[RawDoc]:
    docs = []

    # Open the file
    with open(file, 'r') as file:
        insideDocParagraph = False

        currentParagraph = ""
        currentDeclaration = ""

        for line in file:
            line = line.strip()
            # Clear Byte Order Mask from file
            if line.startswith("ï»¿"):
                line = line[len("ï»¿"):]
            if line.startswith("\ufeff"):
                line = line[len("\ufeff"):]

            # Double check for missing format char
            if not line.startswith("///") and '///' in line:
                logging.warning(f"Line contains /// but doesn't start with : {line=} \n first char is {line[0]}")
                line = '///' + line.split('///')[1]

            # Append any comment inside /// to currentParagraph
            if line.startswith("///"):
                if insideDocParagraph:
                    currentParagraph += "\n"
                else:
                    insideDocParagraph = True

                currentParagraph += line[3:].strip()  # Remove the '///'


            # If no comment but we were in a comment before, find the associated class / struct / function
            elif insideDocParagraph:
                if line.__contains__('{'):
                    currentDeclaration += line.split('{')[0]  # Get the name before the line
                    docs.append(RawDoc(currentDeclaration, currentParagraph))

                    # Reset value
                    insideDocParagraph = False
                    currentParagraph = ""
                    currentDeclaration = ""

                # Keep track of everything until the associated class / struct / function is found
                else:
                    currentDeclaration += line

    return docs
