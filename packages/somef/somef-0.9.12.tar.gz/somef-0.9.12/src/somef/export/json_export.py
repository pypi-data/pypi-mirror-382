import json
import re
from datetime import datetime
import yaml
from dateutil import parser as date_parser
from ..utils import constants
from ..regular_expressions import detect_license_spdx,extract_scholarly_article_natural, extract_scholarly_article_properties
from typing import List, Dict

def save_json_output(repo_data, out_path, missing, pretty=False):
    """
    Function that saves the final json Object in the output file
    Parameters
    ----------
    @param repo_data: dictionary with the metadata to be saved
    @param out_path: output path where to save the JSON
    @param missing: print the categories SOMEF was not able to find
    @param pretty: format option to print the JSON in a human-readable way

    Returns
    -------
    @return: Does not return a value
    """
    print("Saving json data to", out_path)
    if missing:
        # add a new key-value papir to the dictionary
        repo_data[constants.CAT_MISSING] = create_missing_fields(repo_data)
    with open(out_path, 'w') as output:
        if pretty:
            json.dump(repo_data, output, sort_keys=True, indent=2)
        else:
            json.dump(repo_data, output)


def save_codemeta_output(repo_data, outfile, pretty=False, requirements_mode='all'):
    """
    Function that saves a Codemeta JSONLD file with a summary of the results

    Parameters
    ----------
    @param repo_data: JSON with the results to translate to Codemeta
    @param outfile: path where to save the codemeta file
    @param pretty: option to show the JSON results in a nice format
    @param requriments_mode: option to show all requriments or just machine readable
    """
    def format_date(date_string):
        date_object = date_parser.parse(date_string)
        return date_object.strftime("%Y-%m-%d")

    # latest_release = None
    # releases = data_path(["releases", "excerpt"])
    #
    # if releases is not None and len(releases) > 0:
    #     latest_release = releases[0]
    #     latest_pub_date = date_parser.parse(latest_release["datePublished"])
    #     for index in range(1, len(releases)):
    #         release = releases[index]
    #         pub_date = date_parser.parse(release["datePublished"])
    #
    #         if pub_date > latest_pub_date:
    #             latest_release = release
    #             latest_pub_date = pub_date

    # def release_path(path):
    #     return DataGraph.resolve_path(latest_release, path)
    code_repository = None
    if constants.CAT_CODE_REPOSITORY in repo_data:
        code_repository = repo_data[constants.CAT_CODE_REPOSITORY][0][constants.PROP_RESULT][constants.PROP_VALUE]

    author_name = None
    if constants.CAT_OWNER in repo_data:
        author_name = repo_data[constants.CAT_OWNER][0][constants.PROP_RESULT][constants.PROP_VALUE]
    
    # add a check for the existence of the 'description' property, similar way to most properties in the method.
    descriptions = None
    if constants.CAT_DESCRIPTION in repo_data:
        descriptions = repo_data[constants.CAT_DESCRIPTION]

    descriptions_text = []
    if descriptions is not None:

        # priority descriptions: Codemeta, without codemeta but confidence 1, rest
        codemeta_desc = [d for d in descriptions if d.get("technique") == "code_parser" and "codemeta.json" in d.get("source", "")]
        github_desc = [d for d in descriptions if d.get("technique") == constants.GITHUB_API]
        readme_desc = [d for d in descriptions if d.get("technique") not in ("code_parser", constants.GITHUB_API)]

        if codemeta_desc:
            # If codemeta just these
            selected = codemeta_desc
        elif github_desc:
            # whitout codemeta, but we have descripciont with confidence 1
            threshold_1 = [d for d in github_desc if d.get("confidence", 0) == 1]
            selected = threshold_1 if threshold_1 else github_desc
        else:
            # Rest of descriptions 
            selected = sorted(readme_desc, key=lambda x: x.get("confidence", 0), reverse=True)[:1]

        flat_descriptions = []
        for d in selected:
            value = d[constants.PROP_RESULT][constants.PROP_VALUE]
            if isinstance(value, list):
                for v in value:
                    if v not in flat_descriptions:
                        flat_descriptions.append(v)
            else:
                if value not in flat_descriptions:
                    flat_descriptions.append(value)

        descriptions_text = flat_descriptions

        # descriptions_text = [d[constants.PROP_RESULT][constants.PROP_VALUE] for d in selected]
        # descriptions.sort(key=lambda x: (x[constants.PROP_CONFIDENCE] + (1 if x[constants.PROP_TECHNIQUE] == constants.GITHUB_API else 0)),
        #                   reverse=True)
        # descriptions_text = [x[constants.PROP_RESULT][constants.PROP_VALUE] for x in descriptions]


    codemeta_output = {
        "@context": "https://w3id.org/codemeta/3.0",
        "@type": "SoftwareSourceCode"
    }
    if constants.CAT_LICENSE in repo_data:
        # We mix the name of the license from github API with the URL of the file (if found)  
        l_result = {}
        is_gitlab = False

        for l in repo_data[constants.CAT_LICENSE]:
            if constants.PROP_NAME in l[constants.PROP_RESULT].keys():
                l_result["name"] = l[constants.PROP_RESULT][constants.PROP_NAME]
            if l[constants.PROP_TECHNIQUE] == "GitLab_API" and l[constants.PROP_RESULT].get("type") == "Url":
                is_gitlab = True               
                l_result["url"] = l[constants.PROP_RESULT][constants.PROP_VALUE]
            
            if is_gitlab:
                if l[constants.PROP_RESULT][constants.PROP_TYPE] == "File_dump":
                    license_info = detect_license_spdx(l[constants.PROP_RESULT][constants.PROP_VALUE], 'CODEMETA')
                    if license_info:
                        l_result["name"] = license_info['name']
                        l_result["identifier"] = license_info['identifier']
                    break

            # checking if PROP_URL is in the keys PROP_RESULT and key "url" is not in results
            if "url" not in l_result.keys() and constants.PROP_URL in l[constants.PROP_RESULT].keys():
                l_result["url"] = l[constants.PROP_RESULT][constants.PROP_URL]
            # else:
            #     print(f"PROP_URL key not found in: {l[constants.PROP_RESULT].keys()}")
        
            # Thist block run if url is not found in the previous 
            if l[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_FILE_EXPLORATION and constants.PROP_SOURCE in l.keys():

                if "url" in l_result and "api.github.com" in l_result["url"]:
                    l_result["url"] = l[constants.PROP_SOURCE]
            else:
                if "url" not in l_result.keys() and constants.PROP_URL in l[constants.PROP_RESULT].keys():
                        l_result["url"] = l[constants.PROP_RESULT][constants.PROP_URL]
            if constants.PROP_SPDX_ID in l[constants.PROP_RESULT].keys():
                l_result["identifier"] = constants.SPDX_BASE + l[constants.PROP_RESULT][constants.PROP_SPDX_ID]
                l_result["spdx_id"] = l[constants.PROP_RESULT][constants.PROP_SPDX_ID]

        codemeta_output["license"] = l_result
    if code_repository is not None:
        codemeta_output["codeRepository"] = code_repository
        codemeta_output["issueTracker"] = code_repository + "/issues"
    if constants.CAT_DATE_CREATED in repo_data:
        value = repo_data[constants.CAT_DATE_CREATED][0][constants.PROP_RESULT][constants.PROP_VALUE]
        if value:
            codemeta_output["dateCreated"] = format_date(value)
    if constants.CAT_DATE_UPDATED in repo_data:
        value = repo_data[constants.CAT_DATE_UPDATED][0][constants.PROP_RESULT][constants.PROP_VALUE]
        if value:
            codemeta_output["dateModified"] = format_date(value)
    if constants.CAT_DOWNLOAD_URL in repo_data:
        codemeta_output["downloadUrl"] = repo_data[constants.CAT_DOWNLOAD_URL][0][constants.PROP_RESULT][constants.PROP_VALUE]
    if constants.CAT_NAME in repo_data:
        codemeta_output["name"] = repo_data[constants.CAT_NAME][0][constants.PROP_RESULT][constants.PROP_VALUE]
    if constants.CAT_LOGO in repo_data:
        codemeta_output["logo"] = repo_data[constants.CAT_LOGO][0][constants.PROP_RESULT][constants.PROP_VALUE]
    if constants.CAT_KEYWORDS in repo_data:
        codemeta_output["keywords"] = repo_data[constants.CAT_KEYWORDS][0][constants.PROP_RESULT][constants.PROP_VALUE]
    if constants.CAT_PROGRAMMING_LANGUAGES in repo_data:
        # Calculate the total code size of all the programming languages
        codemeta_output["programmingLanguage"] = []
        language_data = repo_data.get(constants.CAT_PROGRAMMING_LANGUAGES, [])
        total_size = 0
        for item in language_data:
            result = item.get(constants.PROP_RESULT, {})
            size = result.get(constants.PROP_SIZE)
            if size is not None:
                total_size += size
        # Discard languages below 10% of the total code size, only if size is available
        for item in language_data:
            result = item.get(constants.PROP_RESULT, {})
            size = result.get(constants.PROP_SIZE)
            value = result.get(constants.PROP_VALUE)
            if value not in codemeta_output["programmingLanguage"]:
                if size is not None and value is not None and total_size > 0:
                    percentage = (size / total_size) * 100
                    if percentage > constants.MINIMUM_PERCENTAGE_LANGUAGE_PROGRAMMING:
                        codemeta_output["programmingLanguage"].append(value)
                elif size is None: # when size is not available, it comes from the parsers
                    codemeta_output["programmingLanguage"].append(value)

    if constants.CAT_REQUIREMENTS in repo_data:
        structured_sources = ["pom.xml", "requirements.txt", "setup.py", "environment.yml"]

        code_parser_requirements = []
        seen_structured = set()
        for x in repo_data[constants.CAT_REQUIREMENTS]:
            if x.get(constants.PROP_TECHNIQUE) == constants.TECHNIQUE_CODE_CONFIG_PARSER:
                source = x.get("source", "")
                if any(src in source for src in structured_sources):
                    name = x[constants.PROP_RESULT].get(constants.PROP_NAME) or x[constants.PROP_RESULT].get(constants.PROP_VALUE)
                    version = x[constants.PROP_RESULT].get(constants.PROP_VERSION)
                    key = f"{name.strip()}|{version.strip() if version else ''}"
                    if key not in seen_structured:
                        entry = {"name": name.strip()}
                        if version:
                            entry["version"] = version.strip()
                        code_parser_requirements.append(entry)
                        seen_structured.add(key)

        other_requirements = []
        seen_text = set()
        for x in repo_data[constants.CAT_REQUIREMENTS]:
            if not (
                x.get(constants.PROP_TECHNIQUE) == constants.TECHNIQUE_CODE_CONFIG_PARSER
                and x.get("source") is not None
                and any(src in x["source"] for src in structured_sources)
            ):
                value = x[constants.PROP_RESULT].get(constants.PROP_VALUE, "").strip().replace("\n", " ")
                normalized = " ".join(value.split())
                if normalized not in seen_text:
                    other_requirements.append(value)
                    seen_text.add(normalized)

        if requirements_mode == "v":
            codemeta_output["softwareRequirements"] = code_parser_requirements
        else:
            codemeta_output["softwareRequirements"] = code_parser_requirements + other_requirements

    if constants.CAT_CONTINUOUS_INTEGRATION in repo_data:
        codemeta_output["continuousIntegration"] = repo_data[constants.CAT_CONTINUOUS_INTEGRATION][0][constants.PROP_RESULT][constants.PROP_VALUE]
    # if constants.CAT_WORKFLOWS in repo_data:
    #     codemeta_output["workflows"] = repo_data[constants.CAT_WORKFLOWS][0][constants.PROP_RESULT][constants.PROP_VALUE] 
    if constants.CAT_RELEASES in repo_data:
        
        latest_date = None
        latest_version = None
        latest_description = None
        oldest_date = None
        oldest_version = None

        for l in repo_data[constants.CAT_RELEASES]:
            release_date_str = l[constants.PROP_RESULT].get(constants.PROP_DATE_PUBLISHED)

            if release_date_str:
                release_date = datetime.fromisoformat(release_date_str.replace("Z", "+00:00"))
            
                if latest_date is None or release_date > latest_date:
                    latest_date = release_date
                    latest_version = l[constants.PROP_RESULT].get(constants.PROP_TAG)
                    latest_description = l[constants.PROP_RESULT].get(constants.PROP_DESCRIPTION)

                if oldest_date is None or release_date < oldest_date:
                    oldest_date = release_date
                    oldest_version = l[constants.PROP_RESULT].get(constants.PROP_TAG)

        if latest_description is not None:
            codemeta_output["releaseNotes"] = latest_description
        if latest_version is not None:
            codemeta_output["softwareVersion"] = latest_version
        if oldest_date is not None:
            codemeta_output["datePublished"] = format_date(oldest_date.isoformat())

    install_links = []
    if constants.CAT_INSTALLATION in repo_data:
        for inst in repo_data[constants.CAT_INSTALLATION]:
            if inst[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_HEADER_ANALYSIS and constants.PROP_SOURCE in inst.keys():
                install_links.append(inst[constants.PROP_SOURCE])
            elif inst[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_FILE_EXPLORATION:
                install_links.append(inst[constants.PROP_RESULT][constants.PROP_VALUE])

    if constants.CAT_DOCUMENTATION in repo_data:
        for inst in repo_data[constants.CAT_DOCUMENTATION]:

            if inst[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_HEADER_ANALYSIS and constants.PROP_SOURCE in inst.keys():
                install_links.append(inst[constants.PROP_SOURCE])
            elif inst[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_FILE_EXPLORATION or \
                    inst[constants.PROP_TECHNIQUE] == constants.TECHNIQUE_REGULAR_EXPRESSION:
                install_links.append(inst[constants.PROP_RESULT][constants.PROP_VALUE])
    if len(install_links) > 0:
        # remove duplicates and generate codemeta
        install_links = list(set(install_links))
        codemeta_output["buildInstructions"] = install_links
    if constants.CAT_OWNER in repo_data:
        # if user then person, otherwise organization
        type_aux = repo_data[constants.CAT_OWNER][0][constants.PROP_RESULT][constants.PROP_TYPE]
        if type_aux == "User":
            type_aux = "Person"
        codemeta_output["author"] = [
            {
                "@type": type_aux,
                "@id": "https://github.com/" + author_name
            }
        ]
    if constants.CAT_AUTHORS in repo_data:
        if "author" not in codemeta_output:
            codemeta_output["author"] = []

        for author in repo_data[constants.CAT_AUTHORS]:
            value_author = author[constants.PROP_RESULT].get(constants.PROP_VALUE)
            name_author = author[constants.PROP_RESULT].get(constants.PROP_NAME)
            if value_author and re.search(constants.REGEXP_LTD_INC, value_author, re.IGNORECASE):
                type_author = "Organization"
            else:
                type_author = "Person"

            author_l = {
                "@type": type_author
            }

            if type_author == "Organization":
                if name_author:
                    author_l['name'] = name_author
            else:
                family_name = None
                given_name = None

                if author[constants.PROP_RESULT].get('last_name'):
                    family_name = author[constants.PROP_RESULT].get('last_name')
                    author_l['familyName'] = family_name
                if author[constants.PROP_RESULT].get('given_name'):
                    given_name = author[constants.PROP_RESULT].get('given_name')
                    author_l['givenName'] = given_name 
                if author[constants.PROP_RESULT].get('email'):
                    mail_author = author[constants.PROP_RESULT].get('email')
                    author_l['email'] = mail_author  

                author_l['name'] = name_author

            codemeta_output["author"].append(author_l)

    if constants.CAT_CITATION in repo_data:
        # url_cit = []
        codemeta_output["referencePublication"] = []
        all_reference_publications = []
        # scholarlyArticles = {}
        author_orcids = {}

        for cit in repo_data[constants.CAT_CITATION]:
            scholarlyArticle = {"@type": "ScholarlyArticle"} 

            doi = None
            title = None
            is_bibtex = False

            if constants.PROP_FORMAT in cit[constants.PROP_RESULT] and cit[constants.PROP_RESULT][constants.PROP_FORMAT] == "cff":
                yaml_content = yaml.safe_load(cit[constants.PROP_RESULT]["value"])
                preferred_citation = yaml_content.get("preferred-citation", {})
                doi = yaml_content.get("doi") or preferred_citation.get("doi")
                identifiers = yaml_content.get("identifiers", [])
                url_citation = preferred_citation.get("url") or yaml_content.get("url")
                identifier_url = next((id["value"] for id in identifiers if id["type"] == "url"), None)
                identifier_doi = next((id["value"] for id in identifiers if id["type"] == "doi"), None)

                authors = yaml_content.get("authors", [])

                title = normalize_title(preferred_citation.get("title") or yaml_content.get("title"))

                if identifier_doi:
                    final_url = f"https://doi.org/{identifier_doi}"
                elif doi:
                    final_url = f"https://doi.org/{doi}"
                elif identifier_url:
                    final_url = identifier_url
                elif url_citation:
                    final_url = url_citation
                else:
                    final_url = ''

                scholarlyArticle[constants.PROP_NAME] = title 
                scholarlyArticle[constants.CAT_IDENTIFIER] = doi 
                scholarlyArticle[constants.PROP_URL] = final_url

                author_list = []
                for author in authors:
                    family_name = author.get("family-names")
                    given_name = author.get("given-names")
                    orcid = author.get("orcid")
                    name = author.get("name")

                    if family_name and given_name:
                        author_entry = {
                            "@type": "Person",
                            "familyName": family_name,
                            "givenName": given_name
                        }
                        if orcid:
                            if not orcid.startswith("http"):  # check if orcid is a url
                                orcid = f"https://orcid.org/{orcid}"
                            author_entry["@id"] = orcid
                    elif name:
                        # If there is only a name, we assume this to be an Organization.
                        # it could be not enough acurate

                        author_entry = {
                            "@type": "Organization",
                            "name": name
                        }

                    if family_name and given_name and orcid:
                        key = (family_name.lower(), given_name.lower())
                        author_orcids[key] = orcid

                    author_list.append({k: v for k, v in author_entry.items() if v is not None})  

                if author_list:
                    scholarlyArticle[constants.PROP_AUTHOR] = author_list 
            else:
                if constants.PROP_DOI in cit[constants.PROP_RESULT].keys():
                    doi = cit[constants.PROP_RESULT][constants.PROP_DOI]
                    scholarlyArticle[constants.CAT_IDENTIFIER] = cit[constants.PROP_RESULT][constants.PROP_DOI]

                if constants.PROP_URL in cit[constants.PROP_RESULT].keys():
                    scholarlyArticle[constants.PROP_URL] = cit[constants.PROP_RESULT][constants.PROP_URL]

                if constants.PROP_TITLE in cit[constants.PROP_RESULT].keys():
                    title = normalize_title(cit[constants.PROP_RESULT][constants.PROP_TITLE])
                    scholarlyArticle[constants.PROP_NAME] = cit[constants.PROP_RESULT][constants.PROP_TITLE]    

                if constants.PROP_ORIGINAL_HEADER in cit[constants.PROP_RESULT].keys():
                    if cit[constants.PROP_RESULT][constants.PROP_ORIGINAL_HEADER] == "Citation":
                        if constants.PROP_SOURCE in cit.keys():
                            scholarlyArticle[constants.PROP_URL] = cit[constants.PROP_SOURCE]

                is_bibtex = True

            if len(scholarlyArticle) > 1:  
                # look por information in values as pagination, issn and others
                if re.search(r'@\w+\{', cit[constants.PROP_RESULT][constants.PROP_VALUE]):  
                    scholarlyArticle = extract_scholarly_article_properties(cit[constants.PROP_RESULT][constants.PROP_VALUE], scholarlyArticle, 'CODEMETA')
                else:
                    scholarlyArticle = extract_scholarly_article_natural(cit[constants.PROP_RESULT][constants.PROP_VALUE], scholarlyArticle, 'CODEMETA')

                all_reference_publications.append({
                    **scholarlyArticle,
                    "_source_format": "cff" if not is_bibtex else "bibtex"
                })

        for article in all_reference_publications:
            if "author" in article:
                for author in article["author"]:
                    family_name = author.get("familyName", "").strip()
                    given_name = author.get("givenName", "").strip()
                    key = (family_name.lower(), given_name.lower()) if given_name else None

                    if key and key in author_orcids:
                        author["@id"] = author_orcids[key]  
     
        codemeta_output["referencePublication"] = deduplicate_publications(all_reference_publications)
                # key = (doi, title)

                # if key in scholarlyArticles:
                #     if is_bibtex:
                #         codemeta_output["referencePublication"].remove(scholarlyArticles[key])
                #         codemeta_output["referencePublication"].append(scholarlyArticle)
                #         scholarlyArticles[key] = scholarlyArticle
                # else:
                #     codemeta_output["referencePublication"].append(scholarlyArticle)
                #     scholarlyArticles[key] = scholarlyArticle
            

    if constants.CAT_STATUS in repo_data:
        url_status = repo_data[constants.CAT_STATUS][0]['result'].get('value', '')
        status = url_status.split('#')[-1] if '#' in url_status else None
        if status:
            codemeta_output["developmentStatus"] = status

    if constants.CAT_IDENTIFIER in repo_data:
        codemeta_output["identifier"] = []

        for identifier in repo_data[constants.CAT_IDENTIFIER]:
          value = identifier[constants.PROP_RESULT][constants.PROP_VALUE]
          if value not in codemeta_output['identifier']:
            codemeta_output["identifier"].append(value)

    if constants.CAT_HOMEPAGE in repo_data:

        # example 
        # homepage_urls = {"http://foo.com", "https://foo.com", "http://bar.com"}
        # Result-->  filtered_urls = {"https://foo.com", "http://bar.com"}
        # Prioritize https

        homepage_urls = {hp[constants.PROP_RESULT][constants.PROP_VALUE].strip()
                 for hp in repo_data[constants.CAT_HOMEPAGE]}
        
        filtered_urls = set()
        roots_with_https = {url[len("https://"):] for url in homepage_urls if url.startswith("https://")}

        for url in homepage_urls:
            root = url.replace("http://", "").replace("https://", "")
            if url.startswith("http://") and root in roots_with_https:
                continue
            filtered_urls.add(url)

        codemeta_output["url"] = list(filtered_urls)

    #     codemeta_output["identifier"] = repo_data[constants.CAT_IDENTIFIER][0][constants.PROP_RESULT][constants.PROP_VALUE]
    if constants.CAT_README_URL in repo_data:
        codemeta_output["readme"] = repo_data[constants.CAT_README_URL][0][constants.PROP_RESULT][constants.PROP_VALUE]
    
    # if "contributors" in repo_data:
    #     codemeta_output["contributor"] = data_path(["contributors", "excerpt"])
    # A person is expected, and we extract text at the moment
    if descriptions_text:
        codemeta_output["description"] = descriptions_text
    # if published_date != "":
    # commenting this out because we cannot assume the last published date to be the published date
    #     codemeta_output["datePublished"] = published_date
    pruned_output = {}

    for key, value in codemeta_output.items():
        if not (value is None or ((isinstance(value, list) or isinstance(value, tuple)) and len(value) == 0)):
            pruned_output[key] = value
    # now, prune out the variables that are None
    save_json_output(pruned_output, outfile, None, pretty=pretty)
   

def create_missing_fields(result):
    """Function to create a small report with the categories SOMEF was not able to find.
    The categories are added to the JSON results. This won't be added if you export TTL or Codemeta"""
    missing = []
    repo_data = result
    # for c in constants.categories_files_header:
    for c in constants.all_categories:
        if c not in repo_data:
            missing.append(c)
    return missing

# def normalize_title(title):
#     return re.sub(r"\s+", " ", title.strip().lower()) if title else None

def normalize_title(title: str) -> str:
    if not title:
        return None
    title = re.sub(r'[{}]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip().lower()


def deduplicate_publications(publications: List[Dict]) -> List[Dict]:
    seen = {}
    for pub in publications:
        # doi = pub.get("identifier", "").lower().strip()
        # doi = (pub.get("identifier") or "").lower().strip()
        doi = extract_doi(pub.get("identifier") or "")
        title = normalize_title(pub.get("name", ""))
        key = (doi, title)
      
        if key not in seen:
            seen[key] = pub
        else:
            existing = seen[key]
            existing_format = existing.get("_source_format", "")
            new_format = pub.get("_source_format", "")
            existing_url = (existing.get("url") or "").lower()
            new_url = (pub.get("url") or "").lower()

            # is_doi_url_existing = existing_url.startswith("https://doi.org/")
            # is_doi_url_new = new_url.startswith("https://doi.org/")
            doi_existing = extract_doi(existing_url)
            # print(f'-----> DOI existing: {doi_existing}')
            doi_new = extract_doi(new_url)
            # print(f'-----> DOI existing: {doi_new}')
            is_doi_url_existing = bool(doi_existing)
            is_doi_url_new = bool(doi_new)

            # Priority CFF
            if existing_format != "cff" and new_format == "cff":
                seen[key] = pub

            # Priority DOI URL
            elif existing_format == new_format:
                if not is_doi_url_existing and is_doi_url_new:
                    seen[key] = pub

    result = []
    for pub in seen.values():
        pub.pop("_source_format", None)
        result.append(pub)

    return result
    

def extract_doi(url: str) -> str:
    if not url:
        return ""

    match = re.search(constants.REGEXP_ALL_DOIS, url, re.IGNORECASE)
    return match.group(0).lower() if match else ""
