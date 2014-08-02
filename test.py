from bs4 import BeautifulSoup

soup = BeautifulSoup('<html><div class="a">sdf</div><div class="b">wr</div></html>');
div = soup.select('div.a,div.b')[0];
print(div.string);
