import re
import csv
import json
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

def is_valid_wikipedia_link(link):
	# Validate if the link is a valid Wikipedia link
	return re.match(r'[A-Za-z\:\/\.]*\/wiki\/[A-Za-z0-9\:\_\!\@\#\$\^\&\*\(\)\_\-\+\=\[\]\{\}\;\'\"\,\<\>\.\?\/]*', link)

def scrape_wikipedia_links(starting_link, n_cycles):
	visited_links = set()
	all_links = []
	current_cycle = 1

	def scrape_links_from_page(link):
		nonlocal all_links
		# Fetch the page content
		response = requests.get(link)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			#print(soup)
			links = []
			for anchor in soup.find_all('a', href=True):
				href = anchor['href']
				if is_valid_wikipedia_link(href):
					#print(href)
					if href.startswith(r'/'):
						links.append(href)
			# Convert the list to an ordered set while preserving order
			ordered_set_links = set(list(OrderedDict.fromkeys(links))[10:20])
			print(ordered_set_links)
			return ordered_set_links
		else:
			print("Enter a valid wiki link")
		return set()
	def process_links(link_set):
		nonlocal visited_links, all_links
		new_links = link_set - visited_links
		visited_links |= new_links
		all_links.extend(new_links)

	if not is_valid_wikipedia_link(starting_link):
		raise ValueError("Invalid Wikipedia link")

	while current_cycle <= n_cycles:
		if re.match(r'^/wiki\/[A-Za-z0-9\:\_\!\@\#\$\^\&\*\(\)\_\-\+\=\[\]\{\}\;\'\"\,\<\>\.\?\/]*', starting_link):
			starting_link = f"https://en.wikipedia.org/{starting_link}"
		print(f"Cycle {current_cycle} - Visiting: {starting_link}")
		links_to_scrape = scrape_links_from_page(starting_link)
		process_links(links_to_scrape)

		# Move to the next link in the list, if available
		if all_links:
			starting_link = all_links.pop(0)
		else:
			break

		current_cycle += 1

	return all_links

def write_to_csv(links, total_count, filename='output.csv'):
	with open(filename, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['Total Count', 'Link'])
		writer.writerow([total_count, ''])  # Empty row to separate total count from links
		for link in links:
			writer.writerow(['', link])

def write_to_json(links, total_count, filename='output.json'):
	with open(filename, 'w') as jsonfile:
		data = {
            'Total Count': total_count,
            'Links': links
        }
		json.dump(data, jsonfile, indent=4)

if __name__ == "__main__":
	try:
		wiki_link = input("Enter a Wikipedia link: ")
		n_cycles = int(input("Enter a valid integer between 1 and 3: "))

		if not 1 <= n_cycles <= 3:
			raise ValueError("Invalid value for n_cycles. Please enter a value between 1 and 3.")

		scraped_links = scrape_wikipedia_links(wiki_link, n_cycles)

		# Optional: Optimize code to avoid visiting already visited links
		unique_links = list(set(scraped_links))
		
		write_to_csv(unique_links, len(scraped_links), 'output.csv')
		write_to_json(unique_links, len(scraped_links), 'output.json')
		if scraped_links:
			print(f"Total Links Found: {len(scraped_links)}")
			print(f"Total Unique Links: {len(unique_links)}")

	except ValueError as e:
		print("Error:", e)
