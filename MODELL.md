This File descibes the concept of the data structure as backend for the ordering tool.

## We need in general:
Depot entries:
	Depotbesteller, ... and probably more orga people

SoLaWi shareholders entry
	-> Nubmer of shares
		if one flag small big
	-> saldo in IV ( strictly poitive mit max capacity of 8 weekly baskets)
	
We need to decide whether the depots store the entries of the people beeing part of it or the shareholders store

Changeable weekly capacity-baskets of products
	-> summed IV of product in basket

SoLaWi products entries:
	flag orderable
	(max number orderable at once)
	flag exchangable
		-> or default 0 interchangeing value (IV) messured in in l Milk or pice Beard or wathever
	flag modular 
		-> period of module time
		-> price in euro (Info only) optional 
	flag sellable
		-> period of module time
		-> price in euro (Info only) optional
Where to put flag sellable with sellingprice if needed?
	list of packagesizes
	
## for the ordering:
momentary order per shareholder
	regulary ordered/ deorderd products 
		-> flag order deorder
		-> point of next possible change (week or day)
	one time products

weekly ordered with timestamp


