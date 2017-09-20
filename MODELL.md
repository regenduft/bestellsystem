This File describes the concept of the data structure in the backend for this ordering tool.

#### We need in general the following entries:
Properties which are embraced are properties which are not necessarily needed.

#### General responsibilities:
-	Admins
-	Oderingadmins ...

#### SoLaWi products entries:
-	flag orderable
-	(max number orderable at once)
-	flag exchangable
-	interchangeing value (IV) messured in in l Milk or pice Beard or watheverand default 0 for not changeable
	flag modular 
		-> flag module or sellable
		-> period of module time
		-> optional price in €

% where to put flag sellable with selling price if needed?

	list of (type, packagesizes) tuples

#### Depot entries:
	Depotbesteller, ... and probably more orga people
	Sharholders of Depot List

% We need to decide whether the depots store the entries of the people being part of it or the shareholders store have an entry with Depot. Mind that we haven some people without Depot or rather picking up form Nussloch directly. I prefer to link shareholders in the depot and have a singlebox holder depot to be more structured and be able to have new depots.

#### SoLaWi shareholders entry
	-> Nubmer of shares (poitive integer or 0,5 for small share)
	-> saldo in IV ( strictly poitive with max capacity of 8 weekly baskets) momentary order included 

ii. When initializing a new one ask for Depot, vegetarian, vegan and sell meat.
	

#### Changeable weekly capacity-baskets/ standard order as collection of products
	amount, (packagesize) and product
	(-> summed IV of product in basket)
	
	
## for the ordering:
#### momentary/ next order per shareholder
	regulary ordered, exchange, deorderd products 
		-> flag order, deorder, exchange
		-> optional expireing date
		-> if module or sellable, point of next possible change (start + period in weeks )
		-> week of next order

	one time products:
		-> sepzial products: 
		   vegtables, with subproducts amount to be enabled for odering
		   bread, with type preference
		-> not per product

ii. multiple week deordering all for vacation, should the flour product sum into saldo?

Weekly ordered with timestamps database per shareholder

## views needed for the packing and ordering process:
 All overviews need to have a present and past version.
#### overview of past orderings per shareholder: 

#### overview of each depot:
	oder per member
	total oder 

#### view total orders of all depots:

#### view total bread order with preferences per depot:

#### view of modular products:
	bread.
	meat.
	hearbs.
	quark.
	cheese??
	.
	.
	.


## comments regarding the interface:

The ii. lines are notes regarding the interface.
We need to decide the date, when the weekly oder is closeing.
An E-Mail should be sent to persons in charge (see secu layer, Depotadmins, Oderingadmins, ...) in PDF format (or excel whatever is best)

#### We need the following security layers.
	Fulladmins
	Depotadmins (push to other depot function with notification to other depotadmin, acess to depot overview, able to change momentary (and last week or all?) odering)
	Oderingadmins (acess to all overviews,Products acess, weekly basket change, full past oderings acess)
	Userlevel (change momentary and regular odering, view last oderings)

