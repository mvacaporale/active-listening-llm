import requests

GOOGLE_DOC_URL = "https://docs.google.com/document/d/{}/export?format=txt"

def get_doc_text(doc_id):

    url = GOOGLE_DOC_URL.format(doc_id)
    response = requests.get(url)

    if response.status_code == 200:
        print("Successfully downloaded prompt from Google doc.")
        return response.text
    else:
        raise RuntimeError(f"Failed to download prompt: {response.status_code}")

ACTOR_PROMPT = get_doc_text(doc_id="1m0ZZLFEqSBYhmaMVuqIKLNLHin-noVQE_XH8AqHo7Ps")
GRADER_PROMPT = get_doc_text(doc_id="1wlMJvEhXl1tWtN81HyfQjA2UyUJFDaY15fXSypTcJXI")

if __name__ == "__main__":
    print(ACTOR_PROMPT)
    print(GRADER_PROMPT)