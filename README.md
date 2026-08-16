this is our mockup of what a solution to P3 of chandigarh police hackathon looks like. 
the requirements , as stated by them, are : 
  1    Multi-Source Data Collection       Ingest Tor .onion listings, public forums, blockchain, phone dumps.     
  2    Intelligent Entity Correlation     Link usernames, crypto wallets, emails, phone numbers, mule accounts.   
  3    Suspicious Activity Detection      Auto-detect drug keywords, high-risk listings, surrogate slang codes.   
  4    Interactive Intelligence Dash      Centralized UI for alerts, trends, line search, and case management.    
  5    Network Visualization              Visual link graph (Marketplace ➔ Telegram Admin ➔ Crypto ➔ Mule A/c).    
  6    Automated Alert Generation         Priority field alerts for high-risk transactions and dead-drops.        
  7    Search & Investigation Support     Fast multi-filter search across aliases, wallet addresses, and text.    
  8    Reporting & Evidence Management    Legally compliant audit logs and court-admissible evidence dossiers.    
  9    Security & Access Control          Role-based access, air-gapped machine manifests, immutable hash logs.   
  10   Scalability & Modularity           Extensible offline pipeline with zero cloud lock-in. 
and , of course, this was coded up with ai. 
i share this project with you all, to critique and read up on how we've (...i've) tried to solve these 10 problems. 
in my own language, i think the solution would go something like : 
slightly fragile code that needs constant maintenance to keep up with all the dark web cat-and-mouse game scrapes the raw data and solves all the impediments. 
same with collection of data from seized phones and tipped off telegram / signal / whatever channel. 
this is the domain of classical law enforcement software, so we don't pretend to reinvent the wheel here. 
the ability to ingest onion links, crypto wallets, and parse large unstructured chats is where we begin. 
we use a small language model to do the same. they have gotten surprisingly useful, and at the same time, even with a modest gpu, can tear through data and be more flexible (comes with drawbacks, of course) than traditional keyword matching or regex or whatever. 
pattern matching is still used for stuff we know is used, like upi, phone ,crypto ids. 
with all these data points, we have also mocked up an entity correlation system, but this is the one im kind of in doubt about the robustness off. 
we use "induction" i.e, feeding large amounts of data to said SLM, and identifying recurring codewords, and upon human feedback, add it to known codewords. 
the dashboard is what you see in the html file. 
network visualization flows naturally from entity correlation. 
alert generation is handeled via ready to go whatsapp generation to auto fill whatever data an investigator flags most important from the surfaced results. 
fuzzy search is available. 
reporting is mocked up as hard wired pdf template filling, but also raw text file is available to send to a scribe directly for custom write ups. 
the security aspect i don't understand fully, but apparently every step can be designed to leave an audit trail via hashes and timestamps where faking it becomes impossible later down the line. 
of course zero cloud dependencies, with the option to expand to locally hosted, larger, more intelligent models via local apis. 

TODO : 
understand our own ai slop system.
make a video explaining all this convincingly.
make the presentation.
(not) get shortlisted. 
