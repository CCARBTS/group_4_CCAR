import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Combobox } from '@/components/ui/combobox';

const countries = [
"Afghanistan", 
"Albania", 
"Algeria", 
"American Samoa", 
"Andorra", 
"Angola", 
"Anguilla", 
"Antarctica", 
"Antigua and Barbuda", 
"Argentina", 
"Armenia", 
"Aruba", 
"Australia", 
"Austria", 
"Azerbaijan", 
"Bahamas", 
"Bahrain", 
"Bailiwick of Guernsey", 
"Bailiwick of Jersey", 
"Bangladesh", 
"Barbados", 
"Belarus", 
"Belgium", 
"Belize", 
"Benin", 
"Bermuda", 
"Bhutan", 
"Bolivia", 
"Bolivia (Plurinational State of)", 
"Bosnia and Herzegovina", 
"Botswana", 
"Brazil", 
"British Indian Ocean Territory", 
"British Virgin Islands", 
"Brunei", 
"Bulgaria", 
"Burkina Faso", 
"Burundi", 
"Cabo Verde", 
"Cambodia", 
"Cameroon", 
"Canada", 
"Canary Islands", 
"Cape Verde", 
"Caribbean Netherlands", 
"Cayman Islands", 
"Central African Republic", 
"Chad", 
"Chile", 
"China", 
"China, Hong Kong Special Administrative Region", 
"China, Macao Special Administrative Region", 
"Christmas Island", 
"Colombia", 
"Comoros", 
"Congo", 
"Cook Islands", 
"Costa Rica", 
"Côte d’Ivoire", 
"Croatia", 
"Cuba", 
"Curacao", 
"Curaçao", 
"Cyprus", 
"Czechia", 
"Czech Republic", 
"Democratic People's Republic of Korea", 
"Democratic Republic of Congo", 
"Democratic Republic of the Congo", 
"Denmark", 
"Djibouti", 
"Dominica", 
"Dominican Republic", 
"East Timor", 
"Ecuador", 
"Egypt", 
"El Salvador", 
"Equatorial Guinea", 
"Eritrea", 
"Estonia", 
"eSwatini", 
"Eswatini", 
"Ethiopia", 
"Falkland Islands", 
"Faroe Islands", 
"Fiji", 
"Finland", 
"France", 
"French Guiana", 
"French Polynesia", 
"Gabon", 
"Gambia", 
"Georgia", 
"Germany", 
"Ghana", 
"Gibraltar", 
"Greece", 
"Greenland", 
"Grenada", 
"Guadeloupe", 
"Guam", 
"Guatemala", 
"Guinea", 
"Guinea-Bissau", 
"Guyana", 
"Haiti", 
"Honduras", 
"Hungary", 
"Iceland", 
"India", 
"Indonesia", 
"Iran", 
"Iran (Islamic Republic of)", 
"Iraq", 
"Ireland", 
"Isle of Man", 
"Israel", 
"Italy", 
"Ivory Coast", 
"Jamaica", 
"Japan", 
"Jordan", 
"Kazakhstan", 
"Kenya", 
"Kiribati", 
"Kuwait", 
"Kyrgyzstan", 
"Lao People's Democratic Republic", 
"Laos", 
"Latvia", 
"Lebanon", 
"Lesotho", 
"Liberia", 
"Libya", 
"Liechtenstein", 
"Lithuania", 
"Luxembourg", 
"Madagascar", 
"Malawi", 
"Malaysia", 
"Maldives", 
"Mali", 
"Malta", 
"Marshall Islands", 
"Martinique", 
"Mauritania", 
"Mauritius", 
"Mayotte", 
"Mexico", 
"Micronesia", 
"Micronesia (Federated States of)", 
"Moldova", 
"Monaco", 
"Mongolia", 
"Montenegro", 
"Montserrat", 
"Morocco", 
"Mozambique", 
"Myanmar", 
"Namibia", 
"Nauru", 
"Nepal", 
"Netherlands", 
"Netherlands Antilles", 
"Netherlands (Kingdom of the)", 
"New Caledonia", 
"New Zealand", 
"Nicaragua", 
"Niger", 
"Nigeria", 
"Niue", 
"Northern Mariana Islands", 
"North Korea", 
"North Macedonia", 
"Norway", 
"Oman", 
"Pakistan", 
"Palau", 
"Palestine", 
"Panama", 
"Papua New Guinea", 
"Paraguay", 
"Peru", 
"Philippines", 
"Poland", 
"Portugal", 
"Puerto Rico", 
"Qatar", 
"Republic of Congo", 
"Republic of Korea", 
"Republic of Moldova", 
"Reunion", 
"Réunion", 
"Romania", 
"Russia", 
"Russian Federation", 
"Rwanda", 
"Saint-Barthelemy", 
"Saint Barthélemy", 
"Saint Helena", 
"Saint Helena, Ascension and Tristan da Cunha", 
"Saint Kitts and Nevis", 
"Saint Lucia", 
"Saint-Martin", 
"Saint Martin (French Part)", 
"Saint Pierre and Miquelon", 
"Saint Vincent and the Grenadines", 
"Samoa", 
"San Marino", 
"Sao Tome and Principe", 
"Saudi Arabia", 
"Senegal", 
"Serbia", 
"Serbia Montenegro", 
"Seychelles", 
"Sierra Leone", 
"Singapore", 
"Sint Maarten", 
"Sint Maarten (Dutch part)", 
"Slovakia", 
"Slovenia", 
"Solomon Islands", 
"Somalia", 
"South Africa", 
"South Korea", 
"South Sudan", 
"Spain", 
"Sri Lanka", 
"State of Palestine", 
"Sudan", 
"Suriname", 
"Sweden", 
"Switzerland", 
"Syria", 
"Syrian Arab Republic", 
"Taiwan", 
"Taiwan (Province of China)", 
"Tajikistan", 
"Tanzania", 
"Thailand", 
"Timor-Leste", 
"Togo", 
"Tokelau", 
"Tonga", 
"Trinidad and Tobago", 
"Tunisia", 
"Turkey", 
"Türkiye", 
"Turkmenistan", 
"Turks and Caicos Islands", 
"Tuvalu", 
"Uganda", 
"Ukraine", 
"United Arab Emirates", 
"United Kingdom", 
"United Kingdom of Great Britain and Northern Ireland", 
"United Republic of Tanzania", 
"United States", 
"United States of America", 
"United States Virgin Islands", 
"Uruguay", 
"Uzbekistan", 
"Vanuatu", 
"Vatican City", 
"Venezuela", 
"Venezuela (Bolivarian Republic of)", 
"Vietnam", 
"Viet Nam", 
"Virgin Islands, U.S.", 
"Wallis and Futuna", 
"Wallis and Futuna Islands", 
"Yemen", 
"Zambia", 
"Zimbabwe"
  // Add more countries as needed
];

const CountryPlotSelector = () => {
  const [selectedCountry, setSelectedCountry] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [plotUrl, setPlotUrl] = useState(null);
  const [filteredCountries, setFilteredCountries] = useState(countries);

  useEffect(() => {
    setFilteredCountries(
      countries.filter((country) =>
        country.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [searchTerm]);

  const handlePlot = async () => {
    if (!selectedCountry) return;

    try {
      const response = await axios.post('http://localhost:3001/api/plot', {
        country: selectedCountry,
      });
      setPlotUrl(response.data.plot_url);
    } catch (error) {
      console.error('Error fetching plot:', error);
    }
  };

  return (

    <div className="max-w-6xl mx-auto p-6 bg-white shadow-lg rounded-xl">
      <h2 className="text-xl font-semibold mb-4">Select a Country to Plot</h2>

      <Combobox value={selectedCountry} onValueChange={setSelectedCountry}>
        <Input
          placeholder="Search country..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="mb-2 w-full text-base py-2"
        />
        <div className="max-h-40 overflow-y-auto border rounded shadow">
          {filteredCountries.map((country) => (
            <div
              key={country}
              onClick={() => {
                setSelectedCountry(country);
                setSearchTerm(country);
              }}
              className="cursor-pointer px-2 py-1 hover:bg-gray-100"
            >
              {country}
            </div>
          ))}
        </div>
      </Combobox>

      <Button className="mt-4" onClick={handlePlot} disabled={!selectedCountry}>
        Plot
      </Button>

      {plotUrl && (
        <Card className="mt-6">
          <CardContent className="p-4">
            <img  src={plotUrl} alt="Plot"
            className="w-full max-h-[700px] object-contain rounded border"
            /> 
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CountryPlotSelector;
